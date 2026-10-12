from sqlalchemy import func, select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.models.venue import Venue

from datetime import datetime

from app.core.enums import EventStatus


class VenueRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, venue_id: int, get_deleted: bool = False) -> Venue | None:
        venue = await self.db.get(Venue, venue_id)
        if venue is None or (not get_deleted and not venue.is_active):
            return None
        return venue

    async def search(
        self,
        *,
        search: str | None,
        city: str | None,
        country: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Venue], int]:
        conditions = [Venue.is_active == True]
        if search:
            conditions.append(Venue.title.icontains(search, autoescape=True))
        if city:
            conditions.append(func.lower(Venue.city) == city.strip().lower())
        if country:
            conditions.append(func.lower(Venue.country) == country.strip().lower())

        statement = (
            select(Venue).where(*conditions).order_by(Venue.title, Venue.id).limit(limit).offset(offset)
        )
        venues = await self.db.scalars(statement)
        total = await self.db.scalar(select(func.count(Venue.id)).where(*conditions))
        return venues.all(), total or 0

    async def create(self, *, title: str, street: str, city: str, country: str) -> Venue:
        venue = Venue(title=title, street=street, city=city, country=country, is_active=True)
        self.db.add(venue)
        await self.db.flush()
        return venue

    async def update(self, *, venue: Venue, data: dict) -> Venue:
        for field, value in data.items():
            setattr(venue, field, value)
        await self.db.flush()
        return venue

    async def delete(self, *, venue: Venue) -> None:
        venue.is_active = False
        await self.db.flush()

    async def has_upcoming_events(self, *, venue_id: int, now: datetime) -> bool:
        statement = select(exists().where(
            Event.venue_id == venue_id,
            Event.is_active == True,
            Event.time > now,
            Event.status != EventStatus.CANCELLED.value,
        ))
        return bool(await self.db.scalar(statement))