from fastapi import APIRouter, Query

from app.core.dependencies import CurrentAdmin, DbSession
from app.core.enums import AuditAction, AuditEntity
from app.schemas.audit_log import AuditLogResponse
from app.services.audit_log import AuditLogService

admin_router = APIRouter(prefix="/admin/audit-logs", tags=["audit-logs", "admin"])


@admin_router.get("/", response_model=list[AuditLogResponse])
async def get_audit_logs(
    current_admin: CurrentAdmin,
    db: DbSession,
    actor_id: int | None = None,
    action: AuditAction | None = None,
    entity_type: AuditEntity | None = None,
    entity_id: int | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return await AuditLogService(db).get_logs(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit,
        offset=offset,
    )