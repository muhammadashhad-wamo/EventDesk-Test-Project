from fastapi import HTTPException, status

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.booking import BookingRepository
from app.repositories.event import EventRepository
from app.schemas.booking import BookingResponse, BookingCreate

from app.core.enums import EventStatus


class BookingService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.events = EventRepository(db)
        self.bookings = BookingRepository(db)

    async def get_my_bookings(self, *, user_id: int) -> list[BookingResponse]:
        db_bookings = await self.bookings.get_user_bookings(user_id=user_id)
        return [BookingResponse.model_validate(b) for b in db_bookings]

    async def book(self, *, user_id: int, event_id: int, data: BookingCreate) -> BookingResponse:
        try:
            event = await self.events.get_by_id_for_update(event_id)

            if event is None or not event.is_active:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

            if event.status != EventStatus.PUBLISHED.value:
                raise HTTPException(status.HTTP_409_CONFLICT, "Event is not open for booking")

            if event.time <= datetime.now(timezone.utc):
                raise HTTPException(status.HTTP_409_CONFLICT, "Event has already started")

            if event.available_tickets_count < data.tickets_count:
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    f"Not enough tickets available ({event.available_tickets_count} left)",
                )

            booking = await self.bookings.get(user_id=user_id, event_id=event_id)
            if booking is not None and booking.is_active:
                raise HTTPException(status.HTTP_409_CONFLICT, "You already have a booking for this event")

            event.available_tickets_count -= data.tickets_count

            if booking is None:
                booking = await self.bookings.create(
                    user_id=user_id,
                    event_id=event_id,
                    tickets_count=data.tickets_count,
                    price_at_booking=event.ticket_price,
                )
            else:
                booking = await self.bookings.reactivate(
                    booking=booking,
                    tickets_count=data.tickets_count,
                    price_at_booking=event.ticket_price,
                )

            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

        return BookingResponse.model_validate(booking)