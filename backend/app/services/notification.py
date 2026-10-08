from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import NotificationType
from app.repositories.notification import NotificationRepository
from app.schemas.notification import NotificationResponse


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