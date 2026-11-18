import asyncio
from typing import Set, Dict, Any
from fastapi import WebSocket

class EventBus:
    def __init__(self):
        self._connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            self._connections.discard(websocket)

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        message = {
            "type": event_type,
            "data": data
        }
        async with self._lock:
            disconnected = []
            for connection in self._connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            for connection in disconnected:
                self._connections.discard(connection)

event_bus = EventBus()
