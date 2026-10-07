from fastapi import APIRouter, status

from app.schemas.event import EventResponse

from app.services.event import EventService

from app.core.dependencies import CurrentUser, CurrentAdmin
from app.core.dependencies import DbSession
from app.core.dependencies import GetViewableEvent

router = APIRouter(prefix="/events", tags=["events"])
admin_router = APIRouter(prefix="/admin/events", tags=["events", "admin"])

@router.get("/", response_model=list[EventResponse])
async def get_published_events(db: DbSession):
    return await EventService(db).get_published_events()

@router.get("/me", response_model=list[EventResponse])
async def get_my_events(user: CurrentUser, db: DbSession):
    return await EventService(db).get_user_events(user=user)

@router.get("/{event_id}", response_model=EventResponse)
async def get_event_by_id(current_user: CurrentUser, event: GetViewableEvent):
    return event

######### Admin routes ###############

@admin_router.get("/", response_model=list[EventResponse])
async def get_all_events(current_admin: CurrentAdmin, db: DbSession):
    return await EventService(db).get_all_events()