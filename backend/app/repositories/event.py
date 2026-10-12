from sqlalchemy import select, update, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload, selectinload

from datetime import datetime, timedelta
from decimal import Decimal

from app.core.enums import EventStatus
from app.models.event import Event
from app.models.tag import Tag
from app.models.venue import Venue
from app.schemas.event_filters import EventFilters

_LOAD_ATTENDEES = selectinload(Event.bookings)

_SORT_COLUMNS = {
    "time": Event.time,
    "price": Event.ticket_price,
    "title": Event.title,
}

class EventRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
            self,
            organizer_id: int,
            time: datetime,
            title: str,
            description: str | None,
            status: str,
            category: str | None,
            ticket_price: Decimal,
            available_tickets_count: int,
            venue: Venue | None = None,
            tags: list[Tag] | None = None,
            is_active: bool = True,    
    ):
        event = Event(
            organizer_id=organizer_id,
            time=time,
            title=title,
            description=description,
            status=status,
            category=category,
            ticket_price=ticket_price,
            available_tickets_count=available_tickets_count,
            venue=venue,
            tags=tags or [],
            is_active=is_active,
        )
        self.db.add(event)
        await self.db.flush()
        # Adding this to eager load required attributes for serialization
        await self.db.refresh(event)
        return event


    async def get_by_id(self, event_id: int, get_deleted: bool = False) -> Event | None:
        db_event = await self.db.get(Event, event_id)
        if db_event is None or (not get_deleted and not db_event.is_active):
            return None
        else:
            return db_event

    async def get_by_id_with_reviews(self, event_id: int) -> Event | None:
        statement = (
            select(Event)
            .where(Event.id == event_id)
            .options(selectinload(Event.reviews))
        )
        return await self.db.scalar(statement)

    async def get_by_id_for_update(self, event_id: int) -> Event | None:
        """
        Loads the event and takes a row lock (SELECT ... FOR UPDATE) that is
        held until the surrounding transaction commits or rolls back.
        """
        statement = (
            select(Event)
            .where(Event.id == event_id)
            .options(lazyload("*"))
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return await self.db.scalar(statement)

    async def search(
        self,
        *,
        filters: EventFilters,
        limit: int,
        offset: int,
        published_only: bool = False,
        organizer_id: int | None = None,
        status: EventStatus | None = None,
        get_deleted: bool = False,
    ) -> tuple[list[Event], int]:
        conditions = []

        if not get_deleted:
            conditions.append(Event.is_active == True)
        if published_only:
            conditions.append(Event.status == EventStatus.PUBLISHED.value)
        if status is not None:
            conditions.append(Event.status == status.value)
        if organizer_id is not None:
            conditions.append(Event.organizer_id == organizer_id)

        if filters.search:
            conditions.append(or_(
                Event.title.icontains(filters.search, autoescape=True),
                Event.description.icontains(filters.search, autoescape=True),
            ))
        if filters.category:
            conditions.append(func.lower(Event.category) == filters.category.strip().lower())
        if filters.venue_id is not None:
            conditions.append(Event.venue_id == filters.venue_id)
        if filters.city:
            conditions.append(Event.venue.has(func.lower(Venue.city) == filters.city.strip().lower()))
        if filters.tags:
            wanted = [t.strip().lower() for t in filters.tags]
            conditions.append(Event.tags.any(Tag.tag.in_(wanted)))
        if filters.min_price is not None:
            conditions.append(Event.ticket_price >= filters.min_price)
        if filters.max_price is not None:
            conditions.append(Event.ticket_price <= filters.max_price)
        if filters.starts_after is not None:
            conditions.append(Event.time >= filters.starts_after)
        if filters.starts_before is not None:
            conditions.append(Event.time <= filters.starts_before)
        if filters.has_tickets is True:
            conditions.append(Event.available_tickets_count > 0)
        elif filters.has_tickets is False:
            conditions.append(Event.available_tickets_count <= 0)

        sort_column = _SORT_COLUMNS[filters.sort_by]
        direction = sort_column.desc() if filters.order == "desc" else sort_column.asc()

        statement = (
            select(Event)
            .where(*conditions)
            .order_by(direction, Event.id)
            .limit(limit)
            .offset(offset)
        )
        events = await self.db.scalars(statement)
        total = await self.db.scalar(select(func.count(Event.id)).where(*conditions))
        return events.all(), total or 0

    async def update(self, *, event: Event, data: dict) -> Event:
        db_event = await self.db.merge(event)

        for field, value in data.items():
            setattr(db_event, field, value)

        await self.db.flush()

        return db_event

    async def delete(self, *, event: Event) -> None:
        db_event = await self.db.merge(event)
        db_event.is_active = False
        await self.db.flush()

    async def get_by_id_with_bookings(self, event_id: int) -> Event | None:
        statement = (
            select(Event)
            .where(Event.id == event_id)
            .options(lazyload("*"), _LOAD_ATTENDEES)
        )
        return await self.db.scalar(statement)

    async def claim_due_for_reminder(self, *, now: datetime, lead_time: timedelta) -> list[Event]:
        statement = (
            select(Event)
            .where(
                Event.is_active == True,
                Event.status == EventStatus.PUBLISHED.value,
                Event.reminder_sent == False,
                Event.time > now,
                Event.time <= now + lead_time,
            )
            .options(lazyload("*"), _LOAD_ATTENDEES)
            .with_for_update(skip_locked=True)
        )
        events = await self.db.scalars(statement)
        return events.all()

    async def mark_past_as_completed(self, *, now: datetime) -> int:
        statement = (
            update(Event)
            .where(Event.status == EventStatus.PUBLISHED.value, Event.time <= now)
            .values(status=EventStatus.COMPLETED.value)
            .execution_options(synchronize_session=False)
        )
        result = await self.db.execute(statement)
        return result.rowcount