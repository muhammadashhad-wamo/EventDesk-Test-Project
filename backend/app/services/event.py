from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.repositories.event import EventRepository
from app.schemas.event import EventResponse


class UserService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.events = EventRepository(db)

    async def get_published_events(self) -> list[EventResponse]:
        db_events = await self.events.get_published()
        return [EventResponse.model_validate(event) for event in db_events]