from fastapi import APIRouter, Query, status

from app.core.dependencies import CurrentUser, DbSession
from app.core.enums import NotificationType
from app.schemas.notification import NotificationResponse, UnreadCountResponse
from app.services.notification import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=list[NotificationResponse])
async def get_my_notifications(
    user: CurrentUser,
    db: DbSession,
    notification_type: NotificationType | None = Query(default=None, alias="type"),
    is_read: bool | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return await NotificationService(db).get_my_notifications(
        user_id=user.id,
        notification_type=notification_type,
        is_read=is_read,
        limit=limit,
        offset=offset,
    )

@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(user: CurrentUser, db: DbSession):
    return await NotificationService(db).get_unread_count(user_id=user.id)

@router.patch("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(user: CurrentUser, db: DbSession):
    await NotificationService(db).mark_all_read(user_id=user.id)

@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_read(notification_id: int, user: CurrentUser, db: DbSession):
    return await NotificationService(db).set_read(
        user_id=user.id, notification_id=notification_id, is_read=True
    )

@router.patch("/{notification_id}/unread", response_model=NotificationResponse)
async def mark_unread(notification_id: int, user: CurrentUser, db: DbSession):
    return await NotificationService(db).set_read(
        user_id=user.id, notification_id=notification_id, is_read=False
    )