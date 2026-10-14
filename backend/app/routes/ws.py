import asyncio
import json
from collections.abc import Awaitable, Callable

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.realtime.auth import authenticate_websocket, get_viewable_ticket_count
from app.realtime.manager import manager

from app.core.config import settings

router = APIRouter(tags=["realtime"])


async def _receive_token(websocket: WebSocket) -> str | None:
    try:
        raw = await asyncio.wait_for(websocket.receive_text(), timeout=settings.WEBSOCKET_AUTH_TIMEOUT_SECONDS)
    except (asyncio.TimeoutError, WebSocketDisconnect):
        return None
    if len(raw) > settings.WEBSOCKET_MAX_MESSAGE_CHARS:
        return None
    try:
        message = json.loads(raw)
    except ValueError:
        return None
    if not isinstance(message, dict) or message.get("type") != "auth":
        return None
    token = message.get("token")
    return token if isinstance(token, str) else None


async def _listen(websocket: WebSocket, still_valid: Callable[[], Awaitable[bool]]) -> None:
    loop = asyncio.get_running_loop()
    last_activity = loop.time()
    last_check = loop.time()

    while True:
        try:
            raw = await asyncio.wait_for(websocket.receive_text(), timeout=settings.WEBSOCKET_RECHECK_INTERVAL_SECONDS)
        except asyncio.TimeoutError:
            raw = None

        now = loop.time()
        if raw is not None:
            if len(raw) > settings.WEBSOCKET_MAX_MESSAGE_CHARS:
                await websocket.close(code=status.WS_1009_MESSAGE_TOO_BIG)
                return
            last_activity = now
        elif now - last_activity >= settings.WEBSOCKET_IDLE_TIMEOUT_SECONDS:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        if now - last_check >= settings.WEBSOCKET_RECHECK_INTERVAL_SECONDS:
            if not await still_valid():
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            last_check = now


@router.websocket("/ws/events/{event_id}")
async def event_updates(websocket: WebSocket, event_id: int):
    await websocket.accept()
    try:
        token = await _receive_token(websocket)
        user = await authenticate_websocket(token) if token else None
        snapshot = await get_viewable_ticket_count(user, event_id) if user else None
        if snapshot is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        async def still_valid() -> bool:
            current = await authenticate_websocket(token)
            return current is not None and await get_viewable_ticket_count(current, event_id) is not None

        manager.subscribe_event(event_id, websocket)
        await websocket.send_json(
            {"type": "tickets_updated", "event_id": event_id, "available_tickets_count": snapshot}
        )
        await _listen(websocket, still_valid)
    except WebSocketDisconnect:
        pass
    finally:
        manager.unsubscribe_event(event_id, websocket)


@router.websocket("/ws/notifications")
async def notification_updates(websocket: WebSocket):
    await websocket.accept()
    user = None
    try:
        token = await _receive_token(websocket)
        user = await authenticate_websocket(token) if token else None
        if user is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        async def still_valid() -> bool:
            return await authenticate_websocket(token) is not None

        manager.register_user(user.id, websocket)
        await _listen(websocket, still_valid)
    except WebSocketDisconnect:
        pass
    finally:
        if user is not None:
            manager.unregister_user(user.id, websocket)