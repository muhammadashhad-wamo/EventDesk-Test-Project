from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import NotificationType


class NotificationCreate(BaseModel):
    user_id: int
    type: NotificationType
    message: str
    event_id: int | None = None


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    message: str
    event_id: int | None
    is_read: bool
    created_at: datetime