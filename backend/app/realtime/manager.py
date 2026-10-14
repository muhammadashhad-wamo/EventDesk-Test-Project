import asyncio
import logging
from collections import defaultdict

from fastapi import WebSocket

from app.core.config import settings

logger = logging.getLogger(__name__)


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
        results = await asyncio.gather(*(self._safe_send(ws, message) for ws in sockets))
        dead = [ws for ws, ok in zip(sockets, results) if not ok]
        if dead:
            await asyncio.gather(*(self._drop(ws) for ws in dead))

    @staticmethod
    async def _safe_send(websocket: WebSocket, message: dict) -> bool:
        try:
            await asyncio.wait_for(websocket.send_json(message), timeout=settings.WEBSOCKET_SEND_TIMEOUT_SECONDS)
            return True
        except asyncio.TimeoutError:
            logger.warning(
                "WebSocket send timed out after %ss (message type=%s)",
                settings.WEBSOCKET_SEND_TIMEOUT_SECONDS, message.get("type"),
            )
        except Exception:
            logger.warning(
                "WebSocket send failed (message type=%s)", message.get("type"), exc_info=True
            )
        return False

    async def _drop(self, websocket: WebSocket) -> None:
        for event_id in [eid for eid, room in self._event_rooms.items() if websocket in room]:
            self.unsubscribe_event(event_id, websocket)
        for user_id in [uid for uid, socks in self._user_sockets.items() if websocket in socks]:
            self.unregister_user(user_id, websocket)
        try:
            await asyncio.wait_for(websocket.close(), timeout=settings.WEBSOCKET_SEND_TIMEOUT_SECONDS)
        except Exception:
            pass


manager = ConnectionManager()