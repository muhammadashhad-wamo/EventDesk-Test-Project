from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import NotificationType
from app.repositories.notification import NotificationRepository
from app.schemas.notification import NotificationResponse, UnreadCountResponse


class NotificationService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.notifications = NotificationRepository(db)

    async def get_my_notifications(
        self,
        *,
        user_id: int,
        notification_type: NotificationType | None,
        is_read: bool | None,
        limit: int,
        offset: int,
    ) -> list[NotificationResponse]:
        db_notifications = await self.notifications.get_for_user(
            user_id=user_id,
            notification_type=notification_type,
            is_read=is_read,
            limit=limit,
            offset=offset,
        )
        return [NotificationResponse.model_validate(n) for n in db_notifications]

    async def get_unread_count(self, *, user_id: int) -> UnreadCountResponse:
        count = await self.notifications.count_unread(user_id=user_id)
        return UnreadCountResponse(unread_count=count)

    async def mark_all_read(self, *, user_id: int) -> None:
        try:
            await self.notifications.mark_all_read(user_id=user_id)
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

    async def set_read(self, *, user_id: int, notification_id: int, is_read: bool) -> NotificationResponse:
        notification = await self.notifications.get_owned(
            notification_id=notification_id, user_id=user_id
        )
        if notification is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")

        try:
            notification = await self.notifications.set_read(notification=notification, is_read=is_read)
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

        return NotificationResponse.model_validate(notification)