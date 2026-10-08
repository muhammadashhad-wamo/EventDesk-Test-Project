from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.event import EventRepository
from app.repositories.review import ReviewRepository
from app.repositories.booking import BookingRepository
from app.schemas.review import (
    ReviewResponse,
    ReviewCreate,
    ReviewUpdate,
    ReviewBase,
    ReplyCreate,
    ReplyResponse
)
from sqlalchemy.exc import IntegrityError
from app.schemas.user import UserBase

from app.core.enums import UserRole

from app.tasks.notifications import new_review, review_mentions


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

    async def create(self, *, user: UserBase, event_id: int, data: ReviewCreate, background: BackgroundTasks) -> ReviewResponse:
        event = await self.events.get_by_id(event_id=event_id)
        if event is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

        booking = await self.bookings.get(user_id=user.id, event_id=event_id)
        if booking is None or not booking.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only review events you have booked")

        if await self.reviews.exists_for_user_and_event(user_id=user.id, event_id=event_id):
            raise HTTPException(status.HTTP_409_CONFLICT, "You have already reviewed this event")

        organizer_id, event_title = event.organizer_id, event.title

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

        if organizer_id != user.id:
            background.add_task(
                new_review,
                organizer_id=organizer_id,
                event_id=event_id,
                event_title=event_title,
                stars_count=data.stars_count,
            )
        if data.mentioned_user_ids:
            background.add_task(
                review_mentions,
                author_id=user.id,
                user_ids=data.mentioned_user_ids,
                event_id=event_id,
                event_title=event_title,
            )

        return ReviewResponse.model_validate(review)

    async def update(self, *, user: UserBase, review: ReviewBase, data: ReviewUpdate) -> ReviewResponse:
        review = await self.reviews.get_by_id(review_id=review.id)
        update_data = data.model_dump(exclude_unset=True)

        try:
            review = await self.reviews.update(review=review, data=update_data)
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

        return ReviewResponse.model_validate(review)

    async def delete(self, *, review_id: int) -> None:
        review = await self.reviews.get_by_id(review_id=review_id)

        try:
            await self.reviews.delete(review=review)
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

    async def reply(self, *, user: UserBase, review_id: int, data: ReplyCreate) -> ReplyResponse:
        review = await self.reviews.get_by_id(review_id)
        if review is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Review not found")

        if user.role != UserRole.ADMIN and review.event.organizer_id != user.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the event organizer can reply to this review")

        try:
            reply = await self.reviews.add_reply(
                review=review,
                user_id=user.id,
                comment=data.comment,
            )
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

        return ReplyResponse.model_validate(reply)