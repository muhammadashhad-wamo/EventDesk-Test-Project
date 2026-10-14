from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditActorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None
    name: str | None


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_id: int | None
    actor: AuditActorResponse
    action: str
    entity_type: str
    entity_id: int | None
    created_at: datetime