from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.venue import VenueRepository
from app.schemas.pagination import Page, PaginationParams
from app.schemas.venue import VenueResponse


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