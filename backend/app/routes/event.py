from fastapi import APIRouter, status

from app.schemas.event import EventResponse

from app.services.event import EventService

from app.core.dependencies import CurrentUser, CurrentAdmin
from app.core.dependencies import DbSession

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/", response_model=list[EventResponse])
async def get_published_events(db: DbSession):
    return await EventService(db).get_published_events()

@router.get("/me", response_model=list[EventResponse])
async def get_my_events(user: CurrentUser, db: DbSession):
    return await EventService(db).get_user_events(user=user)

