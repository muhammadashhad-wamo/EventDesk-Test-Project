from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AuditAction, AuditEntity
from app.repositories.audit_log import AuditLogRepository
from app.schemas.audit_log import AuditLogResponse


class AuditLogService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.audit = AuditLogRepository(db)

    async def get_logs(
        self,
        *,
        actor_id: int | None,
        action: AuditAction | None,
        entity_type: AuditEntity | None,
        entity_id: int | None,
        limit: int,
        offset: int,
    ) -> list[AuditLogResponse]:
        db_logs = await self.audit.get_all(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit,
            offset=offset,
        )
        return [AuditLogResponse.model_validate(log) for log in db_logs]