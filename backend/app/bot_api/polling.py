import asyncio
import time
from typing import Dict, List, Any, Optional

class BotQueue:
    def __init__(self, bot_id: int):
        self.bot_id = bot_id
        self.updates: List[Dict[str, Any]] = []
        self.event = asyncio.Event()
        self.lock = asyncio.Lock()
        self.is_stopped = False

    def enqueue(self, update: Dict[str, Any]):
        self.updates.append(update)
        self.event.set()

    def acknowledge(self, offset: int):
        """Discards all updates with update_id < offset."""
        self.updates = [u for u in self.updates if u.get("update_id", 0) >= offset]

    def stop(self):
        self.is_stopped = True
        self.event.set()

    def reset(self):
        self.is_stopped = False
        self.event.clear()

class UpdateQueueManager:
    def __init__(self):
        self._queues: Dict[int, BotQueue] = {}
        self._global_lock = asyncio.Lock()

    async def get_queue(self, bot_id: int) -> BotQueue:
        async with self._global_lock:
            if bot_id not in self._queues:
                self._queues[bot_id] = BotQueue(bot_id)
            return self._queues[bot_id]

    async def enqueue_update(self, bot_id: int, update: Dict[str, Any]):
        queue = await self.get_queue(bot_id)
        queue.enqueue(update)

    async def stop_bot(self, bot_id: int):
        queue = await self.get_queue(bot_id)
        queue.stop()

    async def start_bot(self, bot_id: int):
        queue = await self.get_queue(bot_id)
        queue.reset()

    async def get_updates(
        self,
        bot_id: int,
        offset: Optional[int] = None,
        limit: int = 100,
        timeout: int = 0,
        allowed_updates: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        queue = await self.get_queue(bot_id)

        async with queue.lock:
            # 1. Acknowledge old updates
            if offset is not None:
                queue.acknowledge(offset)

            start_time = time.time()
            limit = max(1, min(limit, 100))

            while True:
                if queue.is_stopped:
                    return []

                # Filter updates
                filtered = []
                for u in queue.updates:
                    uid = u.get("update_id", 0)
                    if offset is not None and uid < offset:
                        continue
                    if allowed_updates:
                        # Check if any allowed key exists in update (e.g. "message", "callback_query")
                        keys = set(u.keys()) - {"update_id"}
                        if not any(k in allowed_updates for k in keys):
                            continue
                    filtered.append(u)

                if filtered:
                    return filtered[:limit]

                if timeout <= 0:
                    return []

                elapsed = time.time() - start_time
                remaining = timeout - elapsed
                if remaining <= 0:
                    return []

                queue.event.clear()
                try:
                    await asyncio.wait_for(queue.event.wait(), timeout=remaining)
                except asyncio.TimeoutError:
                    return []

update_queue_manager = UpdateQueueManager()
