import pytest
import asyncio
from pathlib import Path
from backend.app.services.process_manager import process_manager
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.bot import Bot

@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()

@pytest.mark.asyncio
async def test_process_manager_lifecycle(tmp_path):
    bot_id = 991
    async with AsyncSessionLocal() as session:
        bot = Bot(id=bot_id, name="ProcBot", username="proc_bot", token="991:TOKEN")
        session.add(bot)
        await session.commit()

    # Create dummy python script
    script_file = tmp_path / "bot_script.py"
    script_file.write_text(
        "import sys, time\n"
        "print('Bot started successfully!')\n"
        "sys.stdout.flush()\n"
        "time.sleep(10)\n"
    )

    # 1. Start process
    mp = await process_manager.start_process(bot_id, str(script_file))
    assert mp.status == "RUNNING"
    assert mp.pid is not None

    # Wait for stdout output
    await asyncio.sleep(1.0)
    logs = await process_manager.get_logs(bot_id)
    stdout_logs = [l["text"] for l in logs if l["stream"] == "stdout"]
    assert any("Bot started successfully!" in l for l in stdout_logs)

    # 2. Stop process
    stopped = await process_manager.stop_process(bot_id)
    assert stopped is True
    status = await process_manager.get_status(bot_id)
    assert status["status"] == "STOPPED"
