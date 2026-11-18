import asyncio
import os
import sys
import time
import subprocess
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
from sqlalchemy import select

from backend.app.core.config import settings
from backend.app.core.database import AsyncSessionLocal
from backend.app.core.events import event_bus
from backend.app.models.bot import Bot
from backend.app.models.process import ProcessRecord
from backend.app.bot_api.polling import update_queue_manager

class ManagedProcess:
    def __init__(self, bot_id: int, file_path: str, work_dir: Optional[str] = None):
        self.bot_id = bot_id
        self.file_path = file_path
        self.work_dir = work_dir or str(Path(file_path).parent)
        self.process: Optional[subprocess.Popen] = None
        self.status = "STOPPED"  # STOPPED, STARTING, RUNNING, STOPPING, ERROR
        self.pid: Optional[int] = None
        self.exit_code: Optional[int] = None
        self.started_at: Optional[datetime] = None
        self.stopped_at: Optional[datetime] = None
        self.logs: List[Dict[str, Any]] = []
        self.max_logs = 1000

    def add_log(self, stream: str, text: str) -> Dict[str, Any]:
        entry = {
            "bot_id": self.bot_id,
            "timestamp": time.time(),
            "stream": stream,
            "text": text
        }
        self.logs.append(entry)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
        return entry

class ProcessManager:
    def __init__(self):
        self._processes: Dict[int, ManagedProcess] = {}
        self._lock = asyncio.Lock()

    async def get_managed(self, bot_id: int) -> Optional[ManagedProcess]:
        return self._processes.get(bot_id)

    async def get_status(self, bot_id: int) -> Dict[str, Any]:
        mp = self._processes.get(bot_id)
        if not mp:
            return {
                "bot_id": bot_id,
                "status": "STOPPED",
                "file_path": None,
                "work_dir": None,
                "pid": None,
                "exit_code": None,
                "started_at": None,
                "stopped_at": None
            }
        return {
            "bot_id": mp.bot_id,
            "status": mp.status,
            "file_path": mp.file_path,
            "work_dir": mp.work_dir,
            "pid": mp.pid,
            "exit_code": mp.exit_code,
            "started_at": mp.started_at.isoformat() if mp.started_at else None,
            "stopped_at": mp.stopped_at.isoformat() if mp.stopped_at else None
        }

    async def get_logs(self, bot_id: int) -> List[Dict[str, Any]]:
        mp = self._processes.get(bot_id)
        if not mp:
            return []
        return list(mp.logs)

    async def start_process(self, bot_id: int, file_path: str, work_dir: Optional[str] = None) -> ManagedProcess:
        async with self._lock:
            # Check existing
            existing = self._processes.get(bot_id)
            if existing and existing.status in ("RUNNING", "STARTING"):
                if existing.process and existing.process.poll() is None:
                    raise ValueError(f"Process for bot {bot_id} is already running (PID: {existing.pid})")

            # Validate and resolve file path
            clean_path = file_path.strip().strip('"').strip("'")
            file_p = Path(clean_path)
            if not file_p.is_absolute():
                candidate = settings.root_dir / file_p
                if candidate.exists():
                    resolved_path = candidate.resolve()
                else:
                    resolved_path = file_p.resolve()
            else:
                resolved_path = file_p.resolve()

            if not resolved_path.exists():
                raise FileNotFoundError(f"Python script '{file_path}' does not exist (resolved: {resolved_path})")

            resolved_work_dir = work_dir or str(resolved_path.parent)

            mp = ManagedProcess(bot_id, str(resolved_path), resolved_work_dir)
            mp.status = "STARTING"
            self._processes[bot_id] = mp

            await event_bus.broadcast("process_status", await self.get_status(bot_id))
            await update_queue_manager.start_bot(bot_id)

            # Update DB Bot status
            async with AsyncSessionLocal() as session:
                res = await session.execute(select(Bot).where(Bot.id == bot_id))
                bot = res.scalar_one_or_none()
                if bot:
                    bot.is_running = True
                    p_rec = ProcessRecord(
                        bot_id=bot.id,
                        file_path=str(resolved_path),
                        work_dir=mp.work_dir,
                        status="STARTING",
                        started_at=datetime.now(timezone.utc)
                    )
                    session.add(p_rec)
                    await session.commit()

            try:
                env = os.environ.copy()
                env["PYTHONUNBUFFERED"] = "1"
                env["PYTHONIOENCODING"] = "utf-8"

                loop = asyncio.get_running_loop()

                mp.process = subprocess.Popen(
                    [sys.executable, "-u", str(resolved_path)],
                    cwd=mp.work_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    encoding="utf-8",
                    errors="replace"
                )

                mp.pid = mp.process.pid
                mp.status = "RUNNING"
                mp.started_at = datetime.now(timezone.utc)

                log_entry = mp.add_log("system", f"Process started with PID {mp.pid}")
                await event_bus.broadcast("process_log", log_entry)
                await event_bus.broadcast("process_status", await self.get_status(bot_id))

                # Update DB PID
                async with AsyncSessionLocal() as session:
                    res = await session.execute(select(Bot).where(Bot.id == bot_id))
                    bot = res.scalar_one_or_none()
                    if bot:
                        bot.is_running = True
                        await session.commit()

                # Start reader threads for stdout and stderr
                threading.Thread(
                    target=self._pipe_reader_thread,
                    args=(mp, mp.process.stdout, "stdout", loop),
                    daemon=True
                ).start()

                threading.Thread(
                    target=self._pipe_reader_thread,
                    args=(mp, mp.process.stderr, "stderr", loop),
                    daemon=True
                ).start()

                # Start monitor thread
                threading.Thread(
                    target=self._process_monitor_thread,
                    args=(mp, loop),
                    daemon=True
                ).start()

                return mp

            except Exception as e:
                mp.status = "ERROR"
                log_entry = mp.add_log("system", f"Failed to start process: {str(e)}")
                await event_bus.broadcast("process_log", log_entry)
                await event_bus.broadcast("process_status", await self.get_status(bot_id))
                raise

    def _pipe_reader_thread(self, mp: ManagedProcess, pipe, stream_name: str, loop: asyncio.AbstractEventLoop):
        if not pipe:
            return
        try:
            for line in iter(pipe.readline, ''):
                clean_line = line.rstrip('\r\n')
                log_entry = mp.add_log(stream_name, clean_line)
                asyncio.run_coroutine_threadsafe(
                    event_bus.broadcast("process_log", log_entry),
                    loop
                )
        except Exception:
            pass
        finally:
            try:
                pipe.close()
            except Exception:
                pass

    def _process_monitor_thread(self, mp: ManagedProcess, loop: asyncio.AbstractEventLoop):
        if not mp.process:
            return
        try:
            exit_code = mp.process.wait()
            mp.exit_code = exit_code
            mp.stopped_at = datetime.now(timezone.utc)
            mp.status = "ERROR" if exit_code != 0 else "STOPPED"

            log_entry = mp.add_log("system", f"Process exited with code {exit_code}")

            async def finalize_exit():
                await event_bus.broadcast("process_log", log_entry)
                await event_bus.broadcast("process_status", await self.get_status(mp.bot_id))
                await update_queue_manager.stop_bot(mp.bot_id)

                async with AsyncSessionLocal() as session:
                    res = await session.execute(select(Bot).where(Bot.id == mp.bot_id))
                    bot = res.scalar_one_or_none()
                    if bot:
                        bot.is_running = False
                        await session.commit()

            asyncio.run_coroutine_threadsafe(finalize_exit(), loop)
        except Exception:
            pass

    async def stop_process(self, bot_id: int) -> bool:
        mp = self._processes.get(bot_id)
        if not mp or not mp.process:
            return False

        if mp.status in ("STOPPED", "ERROR") or mp.process.poll() is not None:
            mp.status = "STOPPED"
            return True

        mp.status = "STOPPING"
        await event_bus.broadcast("process_status", await self.get_status(bot_id))
        await update_queue_manager.stop_bot(bot_id)

        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._terminate_sync, mp.process)

            mp.status = "STOPPED"
            mp.stopped_at = datetime.now(timezone.utc)
            log_entry = mp.add_log("system", "Process stopped by user")
            await event_bus.broadcast("process_log", log_entry)
            await event_bus.broadcast("process_status", await self.get_status(bot_id))

            async with AsyncSessionLocal() as session:
                res = await session.execute(select(Bot).where(Bot.id == bot_id))
                bot = res.scalar_one_or_none()
                if bot:
                    bot.is_running = False
                    await session.commit()

            return True
        except Exception as e:
            mp.status = "ERROR"
            mp.add_log("system", f"Error stopping process: {str(e)}")
            await event_bus.broadcast("process_status", await self.get_status(bot_id))
            return False

    def _terminate_sync(self, proc: subprocess.Popen):
        try:
            proc.terminate()
            try:
                proc.wait(timeout=3.0)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2.0)
        except Exception:
            pass

    async def restart_process(self, bot_id: int) -> ManagedProcess:
        mp = self._processes.get(bot_id)
        if not mp:
            raise ValueError(f"No existing process record for bot {bot_id}")
        file_path = mp.file_path
        work_dir = mp.work_dir
        await self.stop_process(bot_id)
        await asyncio.sleep(0.5)
        return await self.start_process(bot_id, file_path, work_dir)

process_manager = ProcessManager()
