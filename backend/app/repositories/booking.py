from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime, timezone
from decimal import Decimal

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

    async def create(
        self,
        *,
        user_id: int,
        event_id: int,
        tickets_count: int,
        price_at_booking: Decimal,
    ) -> EventBooking:
        booking = EventBooking(
            user_id=user_id,
            event_id=event_id,
            tickets_count=tickets_count,
            price_at_booking=price_at_booking,
            created_at=datetime.now(timezone.utc),
            is_active=True,
        )
        self.db.add(booking)
        await self.db.flush()
        # Adding this to eager load required attributes for serialization
        await self.db.refresh(booking)
        return booking

    async def reactivate(
        self,
        *,
        booking: EventBooking,
        tickets_count: int,
        price_at_booking: Decimal,
    ) -> EventBooking:
        booking.tickets_count = tickets_count
        booking.price_at_booking = price_at_booking
        booking.created_at = datetime.now(timezone.utc)
        booking.is_active = True
        await self.db.flush()
        return booking

    async def deactivate(self, *, booking: EventBooking) -> EventBooking:
        booking.is_active = False
        await self.db.flush()
        return booking