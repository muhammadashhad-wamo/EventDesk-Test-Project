from fastapi import APIRouter, status, BackgroundTasks

from app.schemas.event import EventResponse, EventUpdate, EventCreate

from app.services.event import EventService

from app.core.dependencies import CurrentUser, CurrentAdmin
from app.core.dependencies import DbSession
from app.core.dependencies import GetViewableEvent, GetEditableEvent

router = APIRouter(prefix="/events", tags=["events"])
admin_router = APIRouter(prefix="/admin/events", tags=["events", "admin"])

@router.get("/", response_model=list[EventResponse])
async def get_published_events(db: DbSession):
    return await EventService(db).get_published_events(get_deleted=False)

@router.get("/me", response_model=list[EventResponse])
async def get_my_events(user: CurrentUser, db: DbSession):
    return await EventService(db).get_user_events(user=user, get_deleted=False)

@router.get("/{event_id}", response_model=EventResponse)
async def get_event_by_id(event: GetViewableEvent):
    return event

@router.patch("/{event_id}", response_model=EventResponse)
async def edit_event_by_id(data: EventUpdate, event: GetEditableEvent, db: DbSession, user: CurrentUser):
    return await EventService(db).update_by_id(id=event.id, data=data, actor=user)

@router.patch("/{event_id}/cancel", response_model=EventResponse)
async def cancel_event_by_id(event: GetEditableEvent, db: DbSession, backgroundtasks: BackgroundTasks, user: CurrentUser):
    return await EventService(db).cancel_event_by_id(id=event.id, background=backgroundtasks, actor=user)

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(data: EventCreate, user: CurrentUser, db: DbSession,):
    return await EventService(db).create(user=user, data=data)

######### Admin routes ###############

@admin_router.get("/", response_model=list[EventResponse])
async def get_all_events(current_admin: CurrentAdmin, db: DbSession):
    return await EventService(db).get_all_events(get_deleted=True)

@admin_router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event_by_id(event_id: int, current_admin: CurrentAdmin, db: DbSession):
    await EventService(db).delete_by_id(id=event_id, actor=current_admin)

@admin_router.get("/published", response_model=list[EventResponse])
async def admin_get_published_events(current_admin: CurrentAdmin, db: DbSession):
    return await EventService(db).get_published_events(get_deleted=True)