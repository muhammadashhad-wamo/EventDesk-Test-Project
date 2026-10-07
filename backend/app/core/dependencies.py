from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserRole
from app.core.security import decode_access_token

from app.db.session import get_db

from app.models.user import User

from app.repositories.user import UserRepository
from app.repositories.event import EventRepository

from app.schemas.user import UserBase
from app.schemas.event import EventBase

from app.core.enums import EventStatus

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbSession,
) -> UserBase:
    credentials_exception = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise credentials_exception

    user = await UserRepository(db).get_by_id(user_id)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is deactivated")
    return UserBase.model_validate(user)


CurrentUser = Annotated[UserBase, Depends(get_current_user)]


def require_roles(*roles: UserRole):
    def checker(current_user: CurrentUser) -> UserBase:
        if current_user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return current_user

    return checker


CurrentAdmin = Annotated[UserBase, Depends(require_roles(UserRole.ADMIN))]


async def get_viewable_event(event_id: int, user: CurrentUser, db: DbSession) -> EventBase:
    db_event = await EventRepository(db).get_by_id(event_id=event_id)

    if db_event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

    if (user.role == UserRole.USER) and (db_event.is_active == False or (user.id != db_event.organizer_id and db_event.status not in (EventStatus.PUBLISHED))):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not allowed to view event")

    return EventBase.model_validate(db_event)

GetViewableEvent = Annotated[EventBase, Depends(get_viewable_event)]


async def get_editable_event(event_id: int, user: CurrentUser, db: DbSession) -> EventBase:
    db_event = await EventRepository(db).get_by_id(event_id=event_id)

    if db_event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

    if (user.role == UserRole.USER) and (db_event.is_active == False or user.id != db_event.organizer_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not allowed to edit event")

    return EventBase.model_validate(db_event)

GetEditableEvent = Annotated[EventBase, Depends(get_editable_event)]