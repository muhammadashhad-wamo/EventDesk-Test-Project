from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.booking import BookingRepository
from app.repositories.event import EventRepository
from app.schemas.booking import BookingResponse


class BookingService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.events = EventRepository(db)
        self.bookings = BookingRepository(db)

    async def get_my_bookings(self, *, user_id: int) -> list[BookingResponse]:
        db_bookings = await self.bookings.get_user_bookings(user_id=user_id)
        return [BookingResponse.model_validate(b) for b in db_bookings]