from fastapi import APIRouter, Query, status

from app.core.dependencies import DbSession
from app.schemas.pagination import Page, Pagination
from app.schemas.venue import VenueResponse
from app.services.venue import VenueService

router = APIRouter(prefix="/venues", tags=["venues"])


@router.get("/", response_model=Page[VenueResponse])
async def list_venues(
    db: DbSession,
    pagination: Pagination,
    search: str | None = Query(None, min_length=1, max_length=100, description="Matches title"),
    city: str | None = Query(None, max_length=50),
    country: str | None = Query(None, max_length=50),
):
    return await VenueService(db).list_venues(
        search=search, city=city, country=country, pagination=pagination
    )


@router.get("/{venue_id}", response_model=VenueResponse)
async def get_venue(venue_id: int, db: DbSession):
    return await VenueService(db).get_venue(venue_id=venue_id)