from datetime import datetime, timezone

from sqlalchemy import exists, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.review import Review
from app.models.review_reply import ReviewReply
from app.models.user import User


class ReviewRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, review_id: int) -> Review | None:
        return await self.db.get(Review, review_id)

    async def get_by_event(
        self, *, event_id: int, limit: int, offset: int
    ) -> tuple[list[Review], int]:
        statement = (
            select(Review)
            .where(Review.event_id == event_id)
            .order_by(Review.created_at.desc(), Review.id.desc())
            .limit(limit)
            .offset(offset)
        )
        reviews = await self.db.scalars(statement)
        total = await self.db.scalar(
            select(func.count(Review.id)).where(Review.event_id == event_id)
        )
        return reviews.all(), total or 0

    async def exists_for_user_and_event(self, *, user_id: int, event_id: int) -> bool:
        statement = select(
            exists().where(Review.user_id == user_id, Review.event_id == event_id)
        )
        return await self.db.scalar(statement)

    async def create(
        self,
        *,
        user: User,
        event_id: int,
        stars_count: int,
        comment: str | None,
    ) -> Review:
        review = Review(
            user=user,
            event_id=event_id,
            stars_count=stars_count,
            comment=comment,
            created_at=datetime.now(timezone.utc),
            replies=[],
        )
        self.db.add(review)
        await self.db.flush()
        return review

    async def update(self, *, review: Review, data: dict) -> Review:
        merged_review = await self.db.merge(review)
        for field, value in data.items():
            setattr(merged_review, field, value)
        await self.db.flush()
        return merged_review

    async def delete(self, *, review: Review) -> None:
        await self.db.delete(review)
        await self.db.flush()

    async def add_reply(self, *, review: Review, user: User, comment: str) -> ReviewReply:
        reply = ReviewReply(
            user=user,
            comment=comment,
            created_at=datetime.now(timezone.utc),
        )
        review.replies.append(reply)
        await self.db.flush()
        return reply

    async def get_reply_by_id(self, reply_id: int) -> ReviewReply | None:
        statement = (
            select(ReviewReply)
            .where(ReviewReply.id == reply_id)
            .options(
                joinedload(ReviewReply.review).joinedload(Review.event),
            )
        )
        result = await self.db.execute(statement)
        return result.unique().scalar_one_or_none()

    async def update_reply(
        self, *, reply: ReviewReply, comment: str
    ) -> ReviewReply:
        reply.comment = comment
        await self.db.flush()
        return reply

    async def delete_reply(self, *, reply: ReviewReply) -> None:
        await self.db.delete(reply)
        await self.db.flush()