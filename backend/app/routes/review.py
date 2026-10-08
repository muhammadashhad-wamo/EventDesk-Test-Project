from fastapi import APIRouter

from app.core.dependencies import DbSession, GetViewableEvent
from app.schemas.review import (
    ReviewResponse,
)
from app.services.review import ReviewService

router = APIRouter(tags=["reviews"])


@router.get("/events/{event_id}/reviews", response_model=list[ReviewResponse])
async def get_event_reviews(event: GetViewableEvent, db: DbSession):
    return await ReviewService(db).get_event_reviews(event_id=event.id)