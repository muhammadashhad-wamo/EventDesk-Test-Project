from pydantic import BaseModel, Field, ConfigDict
from app.core.enums import EventStatus
from typing import Annotated

from datetime import datetime
from decimal import Decimal

from app.schemas.venue import VenueResponse
from app.schemas.user import UserResponse

class EventBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)

    id: int
    title: Annotated[str, Field(min_length=1, max_length=50)]
    organizer: UserResponse
    venue: VenueResponse | None = None
    time: datetime
    description: Annotated[str, Field(min_length=1, max_length=200)]
    status: EventStatus
    category: Annotated[str, Field(min_length=1, max_length=50)]
    ticket_price: Decimal
    available_tickets_count: Annotated[int, Field(ge=0)]
    is_active: bool = True

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
    ticket_price: Decimal
    available_tickets_count: Annotated[int, Field(ge=0)]
    is_active: bool = True