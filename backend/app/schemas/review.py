from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReplyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    review_id: int
    comment: str
    created_at: datetime


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    event_id: int
    stars_count: int
    comment: str | None
    created_at: datetime
    replies: list[ReplyResponse]