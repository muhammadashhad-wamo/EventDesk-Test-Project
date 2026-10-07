from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event


class EventRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, event_id: int) -> Event | None:
        return await self.db.get(Event, event_id)

    async def get_published(self) -> list[Event]:
        statement = select(Event).where(Event.status == "published")
        events = await self.db.scalars(statement)
        return events.all()

    async def get_user_events(self, user_id: int) -> list[Event]:
        statement = select(Event).where(Event.organizer_id == user_id)
        events = await self.db.scalars(statement)
        return events.all()