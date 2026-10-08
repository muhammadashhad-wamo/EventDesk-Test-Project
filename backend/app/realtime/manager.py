import asyncio
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._event_rooms: dict[int, set[WebSocket]] = defaultdict(set)
        self._user_sockets: dict[int, set[WebSocket]] = defaultdict(set)

    def subscribe_event(self, event_id: int, websocket: WebSocket) -> None:
        self._event_rooms[event_id].add(websocket)

    def unsubscribe_event(self, event_id: int, websocket: WebSocket) -> None:
        self._event_rooms[event_id].discard(websocket)
        if not self._event_rooms[event_id]:
            del self._event_rooms[event_id]

    def register_user(self, user_id: int, websocket: WebSocket) -> None:
        self._user_sockets[user_id].add(websocket)

    def unregister_user(self, user_id: int, websocket: WebSocket) -> None:
        self._user_sockets[user_id].discard(websocket)
        if not self._user_sockets[user_id]:
            del self._user_sockets[user_id]

    async def broadcast_to_event(self, event_id: int, message: dict) -> None:
        await self._send_all(list(self._event_rooms.get(event_id, ())), message)

    async def send_to_user(self, user_id: int, message: dict) -> None:
        await self._send_all(list(self._user_sockets.get(user_id, ())), message)

    async def _send_all(self, sockets: list[WebSocket], message: dict) -> None:
        await asyncio.gather(*(self._safe_send(ws, message) for ws in sockets))

    @staticmethod
    async def _safe_send(websocket: WebSocket, message: dict) -> None:
        try:
            await websocket.send_json(message)
        except Exception:
            pass


manager = ConnectionManager()