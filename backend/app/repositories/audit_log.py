from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AuditAction, AuditEntity
from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(
        self,
        *,
        actor_id: int | None = None,
        action: AuditAction | None = None,
        entity_type: AuditEntity | None = None,
        entity_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        statement = select(AuditLog).order_by(AuditLog.created_at.desc(), AuditLog.id.desc())

        if actor_id is not None:
            statement = statement.where(AuditLog.actor_id == actor_id)
        if action is not None:
            statement = statement.where(AuditLog.action == action.value)
        if entity_type is not None:
            statement = statement.where(AuditLog.entity_type == entity_type.value)
        if entity_id is not None:
            statement = statement.where(AuditLog.entity_id == entity_id)

        statement = statement.limit(limit).offset(offset)
        logs = await self.db.scalars(statement)
        return logs.all()