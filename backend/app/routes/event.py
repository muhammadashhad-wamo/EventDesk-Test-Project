from fastapi import APIRouter, status

from app.schemas.event import EventResponse, EventUpdate

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
async def get_event_by_id(event: GetViewableEvent):
    return event

@router.patch("/{event_id}", response_model=EventResponse)
async def edit_event_by_id(data: EventUpdate, event: GetViewableEvent, db: DbSession):
    return await EventService(db).update_by_id(id=event.id, data=data)

######### Admin routes ###############

@admin_router.get("/", response_model=list[EventResponse])
async def get_all_events(current_admin: CurrentAdmin, db: DbSession):
    return await EventService(db).get_all_events()

@admin_router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(event_id: int, current_admin: CurrentAdmin, db: DbSession):
    await EventService(db).delete_by_id(id=event_id)