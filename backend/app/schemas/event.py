from pydantic import BaseModel, Field, ConfigDict
from app.core.enums import EventStatus
from typing import Annotated

from datetime import datetime
from decimal import Decimal

from app.schemas.venue import VenueResponse
from app.schemas.user import UserResponse
from app.schemas.tag import TagResponse

class EventBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)

    id: int
    title: Annotated[str, Field(min_length=1, max_length=50)]
    organizer: UserResponse
    venue_id: int | None = None
    time: datetime
    description: Annotated[str, Field(min_length=1, max_length=200)]
    status: EventStatus
    category: Annotated[str, Field(min_length=1, max_length=50)]
    ticket_price: Annotated[Decimal, Field(ge=0)]
    available_tickets_count: Annotated[int, Field(ge=0)]
    is_active: bool = True

class EventCreate(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)

    title: Annotated[str, Field(min_length=1, max_length=50)]
    time: datetime
    description: Annotated[str, Field(min_length=1, max_length=200)] | None = None
    status: EventStatus = EventStatus.DRAFT
    category: Annotated[str, Field(min_length=1, max_length=50)] | None = None
    ticket_price: Annotated[Decimal, Field(ge=0)]
    available_tickets_count: Annotated[int, Field(ge=0)]
    venue_id: int | None = None
    tag_ids: list[int] = Field(default_factory=list, max_length=20)

class EventUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)

    title: Annotated[str, Field(min_length=1, max_length=50)] | None = None
    time: datetime | None = None
    description: Annotated[str, Field(min_length=1, max_length=200)] | None = None
    status: EventStatus | None = None
    category: Annotated[str, Field(min_length=1, max_length=50)] | None = None
    ticket_price: Annotated[Decimal, Field(ge=0)] | None = None
    available_tickets_count: Annotated[int, Field(ge=0)] | None = None
    venue_id: int | None = None
    tag_ids: list[int] | None = Field(default=None, max_length=20)

class EventResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)

    id: int
    title: Annotated[str, Field(min_length=1, max_length=50)]
    organizer: UserResponse
    venue: VenueResponse | None = None
    time: datetime
    description: Annotated[str, Field(min_length=1, max_length=200)]
    status: EventStatus
    category: Annotated[str, Field(min_length=1, max_length=50)]
    ticket_price: Annotated[Decimal, Field(ge=0)]
    available_tickets_count: Annotated[int, Field(ge=0)]
    is_active: bool = True
    tags: list[TagResponse] = []