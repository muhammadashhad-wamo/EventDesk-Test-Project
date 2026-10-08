from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReplyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    review_id: int
    comment: str
    created_at: datetime

class ReplyCreate(BaseModel):
    comment: str = Field(min_length=1, max_length=200)

class ReviewBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    event_id: int
    stars_count: int
    comment: str | None
    created_at: datetime
    replies: list[ReplyResponse]

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
    mentioned_user_ids: list[int] = Field(default_factory=list, max_length=10)

class ReviewUpdate(BaseModel):
    stars_count: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = Field(default=None, max_length=200)

    @field_validator("stars_count")
    @classmethod
    def stars_not_null(cls, value):
        if value is None:
            raise ValueError("stars_count cannot be null")
        return value