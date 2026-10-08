from datetime import datetime, timezone

from sqlalchemy import select, func, update
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

    async def count_unread(self, *, user_id: int) -> int:
        statement = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        return await self.db.scalar(statement) or 0

    async def mark_all_read(self, *, user_id: int) -> None:
        statement = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True)
            .execution_options(synchronize_session=False)
        )
        await self.db.execute(statement)

    async def get_owned(self, *, notification_id: int, user_id: int) -> Notification | None:
        statement = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        return await self.db.scalar(statement)

    async def set_read(self, *, notification: Notification, is_read: bool) -> Notification:
        notification.is_read = is_read
        await self.db.flush()
        return notification