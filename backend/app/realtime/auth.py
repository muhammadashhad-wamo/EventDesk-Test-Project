import jwt

from app.core.enums import EventStatus, UserRole
from app.core.security import decode_access_token
from app.db.session import AsyncSessionLocal
from app.repositories.event import EventRepository
from app.repositories.user import UserRepository
from app.schemas.user import UserBase


async def authenticate_websocket(token: str | None) -> UserBase | None:
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None

    async with AsyncSessionLocal() as db:
        user = await UserRepository(db).get_by_id(user_id)
        if user is None or not user.is_active:
            return None
        return UserBase.model_validate(user)


async def get_viewable_ticket_count(user: UserBase, event_id: int) -> int | None:
    async with AsyncSessionLocal() as db:
        event = await EventRepository(db).get_by_id(event_id=event_id)
        if event is None:
            return None
        is_published = event.status == EventStatus.PUBLISHED.value
        if user.role != UserRole.ADMIN and not is_published and event.organizer_id != user.id:
            return None
        return event.available_tickets_count