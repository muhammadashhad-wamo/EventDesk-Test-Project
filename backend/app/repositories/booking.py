from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event_booking import EventBooking


class BookingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, *, user_id: int, event_id: int) -> EventBooking | None:
        statement = select(EventBooking).where(
            EventBooking.user_id == user_id,
            EventBooking.event_id == event_id,
        )
        return await self.db.scalar(statement)

    async def get_user_bookings(self, *, user_id: int, active_only: bool = True) -> list[EventBooking]:
        statement = select(EventBooking).where(EventBooking.user_id == user_id)
        if active_only:
            statement = statement.where(EventBooking.is_active == True)
        bookings = await self.db.scalars(statement)
        return bookings.all()