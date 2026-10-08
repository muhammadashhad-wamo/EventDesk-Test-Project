from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.event import EventRepository
from app.repositories.review import ReviewRepository
from app.repositories.booking import BookingRepository
from app.schemas.review import (
    ReviewResponse,
    ReviewCreate,
    ReviewUpdate,
    ReviewBase
)
from sqlalchemy.exc import IntegrityError
from app.schemas.user import UserBase


class ReviewService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.events = EventRepository(db)
        self.reviews = ReviewRepository(db)
        self.bookings = BookingRepository(db)

    async def get_event_reviews(self, *, event_id: int) -> list[ReviewResponse]:
        event = await self.events.get_by_id_with_reviews(event_id)
        if event is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

        return [ReviewResponse.model_validate(review) for review in event.reviews]

    async def create(self, *, user: UserBase, event_id: int, data: ReviewCreate) -> ReviewResponse:
        event = await self.events.get_by_id(event_id=event_id)
        if event is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

        booking = await self.bookings.get(user_id=user.id, event_id=event_id)
        if booking is None or not booking.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only review events you have booked")

        if await self.reviews.exists_for_user_and_event(user_id=user.id, event_id=event_id):
            raise HTTPException(status.HTTP_409_CONFLICT, "You have already reviewed this event")

        try:
            review = await self.reviews.create(
                user_id=user.id,
                event_id=event_id,
                stars_count=data.stars_count,
                comment=data.comment,
            )
            await self._db.commit()
        except IntegrityError:
            await self._db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "You have already reviewed this event")
        except Exception:
            await self._db.rollback()
            raise

        return ReviewResponse.model_validate(review)

    async def update(self, *, user: UserBase, review: ReviewBase, data: ReviewUpdate) -> ReviewResponse:
        update_data = data.model_dump(exclude_unset=True)

        try:
            review = await self.reviews.update(review=review, data=update_data)
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

        return ReviewResponse.model_validate(review)