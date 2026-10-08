from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from app.realtime.auth import authenticate_websocket, get_viewable_ticket_count
from app.realtime.manager import manager

router = APIRouter(tags=["realtime"])


@router.websocket("/ws/events/{event_id}")
async def event_updates(websocket: WebSocket, event_id: int, token: str | None = Query(default=None)):
    user = await authenticate_websocket(token)
    if user is None or await get_viewable_ticket_count(user, event_id) is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    manager.subscribe_event(event_id, websocket)
    try:
        snapshot = await get_viewable_ticket_count(user, event_id)
        await websocket.send_json(
            {"type": "tickets_updated", "event_id": event_id, "available_tickets_count": snapshot}
        )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.unsubscribe_event(event_id, websocket)


@router.websocket("/ws/notifications")
async def notification_updates(websocket: WebSocket, token: str | None = Query(default=None)):
    user = await authenticate_websocket(token)
    if user is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    manager.register_user(user.id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.unregister_user(user.id, websocket)