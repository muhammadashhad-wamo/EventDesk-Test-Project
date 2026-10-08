from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

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