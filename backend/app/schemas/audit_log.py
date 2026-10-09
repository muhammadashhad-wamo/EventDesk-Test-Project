from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditActorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_id: int
    actor: AuditActorResponse
    action: str
    entity_type: str
    entity_id: int
    created_at: datetime