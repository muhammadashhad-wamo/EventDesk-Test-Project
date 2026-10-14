from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.repositories.venue import VenueRepository
from app.schemas.pagination import Page, PaginationParams
from app.schemas.venue import VenueResponse, VenueUpdate, VenueCreate


class VenueService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.venues = VenueRepository(db)

    async def list_venues(
        self,
        *,
        search: str | None,
        city: str | None,
        country: str | None,
        pagination: PaginationParams,
    ) -> Page[VenueResponse]:
        db_venues, total = await self.venues.search(
            search=search,
            city=city,
            country=country,
            limit=pagination.limit,
            offset=pagination.offset,
        )
        return Page[VenueResponse](
            items=[VenueResponse.model_validate(v) for v in db_venues],
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
        )

    async def get_venue(self, *, venue_id: int) -> VenueResponse:
        venue = await self.venues.get_by_id(venue_id)
        if venue is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Venue not found")
        return VenueResponse.model_validate(venue)

    async def create(self, *, data: VenueCreate) -> VenueResponse:
        if await self.venues.exists_duplicate(
            title=data.title, street=data.street, city=data.city, country=data.country
        ):
            raise HTTPException(status.HTTP_409_CONFLICT, "Venue already exists")

        try:
            venue = await self.venues.create(
                title=data.title,
                street=data.street,
                city=data.city,
                country=data.country,
            )
            await self._db.commit()
        except IntegrityError:
            await self._db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Venue already exists")
        return VenueResponse.model_validate(venue)

    async def update(self, *, venue_id: int, data: VenueUpdate) -> VenueResponse:
        venue = await self.venues.get_by_id(venue_id)
        if venue is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Venue not found")

        try:
            venue = await self.venues.update(venue=venue, data=data.model_dump(exclude_none=True))
            await self._db.commit()
        except IntegrityError:
            await self._db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Venue already exists")
        return VenueResponse.model_validate(venue)

    async def delete(self, *, venue_id: int) -> None:
        venue = await self.venues.get_by_id(venue_id)
        if venue is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Venue not found")

        if await self.venues.has_upcoming_events(venue_id=venue_id, now=datetime.now(timezone.utc)):
            raise HTTPException(status.HTTP_409_CONFLICT, "Venue has upcoming events")

        try:
            await self.venues.delete(venue=venue)
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise