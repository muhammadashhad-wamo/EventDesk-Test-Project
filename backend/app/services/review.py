from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.event import EventRepository
from app.schemas.review import (
    ReviewResponse,
)


class ReviewService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.events = EventRepository(db)

    async def get_event_reviews(self, *, event_id: int) -> list[ReviewResponse]:
        event = await self.events.get_by_id_with_reviews(event_id)
        if event is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

        return [ReviewResponse.model_validate(review) for review in event.reviews]