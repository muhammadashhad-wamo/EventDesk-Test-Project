from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from datetime import datetime
from decimal import Decimal

from app.models.event import Event


class EventRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
            self,
            organizer_id: int,
            time: datetime,
            title: str,
            description: str,
            status: str,
            category: str,
            ticket_price: Decimal,
            available_tickets_count: int,
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
            is_active=is_active,
        )
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event, attribute_names=["organizer", "venue"])
        return event


    async def get_by_id(self, event_id: int, get_deleted: bool = False) -> Event | None:
        db_event = await self.db.get(Event, event_id, options=[joinedload(Event.organizer), joinedload(Event.venue)])
        if not get_deleted and db_event.is_active == False:
            return None
        else:
            return db_event

    async def get_published(self, get_deleted: bool = False) -> list[Event]:
        if get_deleted:
            statement = select(Event).where(Event.status == "published").options(joinedload(Event.organizer), joinedload(Event.venue))
        else:
            statement = select(Event).where(Event.status == "published", Event.is_active == True).options(joinedload(Event.organizer), joinedload(Event.venue))
        events = await self.db.scalars(statement)
        return events.all()

    async def get_user_events(self, user_id: int, get_deleted: bool = False) -> list[Event]:
        if get_deleted:
            statement = select(Event).where(Event.organizer_id == user_id).options(joinedload(Event.organizer), joinedload(Event.venue))
        else:
            statement = select(Event).where(Event.organizer_id == user_id, Event.is_active == True).options(joinedload(Event.organizer), joinedload(Event.venue))
        events = await self.db.scalars(statement)
        return events.all()

    async def get_all_events(self, get_deleted: bool = False) -> list[Event]:
        if get_deleted:
            statement = select(Event).options(joinedload(Event.organizer), joinedload(Event.venue))
        else:
            statement = select(Event).where(Event.is_active == True).options(joinedload(Event.organizer), joinedload(Event.venue))
        events = await self.db.scalars(statement)
        return events.all()

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