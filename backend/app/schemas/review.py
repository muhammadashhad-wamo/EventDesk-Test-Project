from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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


class ReviewCreate(BaseModel):
    stars_count: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=200)