from fastapi import APIRouter, Query, status

from app.core.dependencies import DbSession, CurrentAdmin
from app.schemas.pagination import Page, Pagination
from app.schemas.venue import VenueResponse, VenueCreate, VenueUpdate
from app.services.venue import VenueService

router = APIRouter(prefix="/venues", tags=["venues"])
admin_router = APIRouter(prefix="/admin/venues", tags=["venues", "admin"])


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


######### Admin routes ###############

@admin_router.post("/", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
async def create_venue(data: VenueCreate, current_admin: CurrentAdmin, db: DbSession):
    return await VenueService(db).create(data=data)


@admin_router.patch("/{venue_id}", response_model=VenueResponse)
async def update_venue(venue_id: int, data: VenueUpdate, current_admin: CurrentAdmin, db: DbSession):
    return await VenueService(db).update(venue_id=venue_id, data=data)


@admin_router.delete("/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_venue(venue_id: int, current_admin: CurrentAdmin, db: DbSession):
    await VenueService(db).delete(venue_id=venue_id)