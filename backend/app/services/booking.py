from fastapi import HTTPException, status, BackgroundTasks

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.booking import BookingRepository
from app.repositories.event import EventRepository
from app.repositories.audit_log import AuditLogRepository
from app.schemas.booking import BookingResponse, BookingCreate

from app.core.enums import EventStatus, AuditAction, AuditEntity

from app.tasks.notifications import booking_confirmed, booking_cancelled

from app.realtime.manager import manager


class BookingService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.events = EventRepository(db)
        self.bookings = BookingRepository(db)
        self.audit = AuditLogRepository(db)

    async def get_my_bookings(self, *, user_id: int) -> list[BookingResponse]:
        db_bookings = await self.bookings.get_user_bookings(user_id=user_id)
        return [BookingResponse.model_validate(b) for b in db_bookings]

    async def book(self, *, user_id: int, event_id: int, data: BookingCreate, background: BackgroundTasks) -> BookingResponse:
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

            await self.audit.create(
                actor_id=user_id,
                action=AuditAction.BOOKING_CREATED,
                entity_type=AuditEntity.EVENT,
                entity_id=event_id,
            )

            event_title = event.title
            available = event.available_tickets_count

            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

        background.add_task(
            booking_confirmed,
            user_id=user_id,
            event_id=event_id,
            event_title=event_title,
            tickets_count=data.tickets_count,
        )
        background.add_task(
            manager.broadcast_to_event,
            event_id,
            {"type": "tickets_updated", "event_id": event_id, "available_tickets_count": available},
        )

        return BookingResponse.model_validate(booking)

    async def cancel(self, *, actor_id: int, user_id: int, event_id: int, background: BackgroundTasks) -> BookingResponse:
        try:
            event = await self.events.get_by_id_for_update(event_id)
            if event is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

            booking = await self.bookings.get(user_id=user_id, event_id=event_id)
            if booking is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")

            if not booking.is_active:
                raise HTTPException(status.HTTP_409_CONFLICT, "Booking is already cancelled")

            if event.time <= datetime.now(timezone.utc):
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    "Cannot cancel a booking for an event that has already started",
                )

            event.available_tickets_count += booking.tickets_count
            await self.bookings.deactivate(booking=booking)

            await self.audit.create(
                actor_id=actor_id,
                action=AuditAction.BOOKING_CANCELLED,
                entity_type=AuditEntity.EVENT,
                entity_id=event_id,
            )

            event_title = event.title
            available = event.available_tickets_count

            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

        background.add_task(
            booking_cancelled,
            user_id=user_id,
            event_id=event_id,
            event_title=event_title,
        )
        background.add_task(
            manager.broadcast_to_event,
            event_id,
            {"type": "tickets_updated", "event_id": event_id, "available_tickets_count": available},
        )

        return BookingResponse.model_validate(booking)