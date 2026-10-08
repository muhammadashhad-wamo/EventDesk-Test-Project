from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import NotificationType
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate


class NotificationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_for_user(
        self,
        *,
        user_id: int,
        notification_type: NotificationType | None = None,
        is_read: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Notification]:
        statement = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
        )
        if notification_type is not None:
            statement = statement.where(Notification.type == notification_type.value)
        if is_read is not None:
            statement = statement.where(Notification.is_read == is_read)

        statement = statement.limit(limit).offset(offset)
        notifications = await self.db.scalars(statement)
        return notifications.all()