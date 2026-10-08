from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    event_id: int
    tickets_count: int
    price_at_booking: Decimal
    created_at: datetime
    is_active: bool