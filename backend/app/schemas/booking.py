from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.event import EventResponse

class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    event_id: int
    tickets_count: int
    price_at_booking: Decimal
    created_at: datetime
    is_active: bool

class BookingCreate(BaseModel):
    tickets_count: int = Field(gt=0)

class BookingUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

class BookingDetailResponse(BookingResponse):
    user: BookingUserResponse
    event: EventResponse

class MyBookingResponse(BookingResponse):
    event: EventResponse