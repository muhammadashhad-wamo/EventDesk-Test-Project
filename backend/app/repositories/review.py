from datetime import datetime, timezone

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.models.review_reply import ReviewReply


class ReviewRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, review_id: int) -> Review | None:
        return await self.db.get(Review, review_id)

    async def exists_for_user_and_event(self, *, user_id: int, event_id: int) -> bool:
        statement = select(
            exists().where(Review.user_id == user_id, Review.event_id == event_id)
        )
        return await self.db.scalar(statement)

    async def create(
        self,
        *,
        user_id: int,
        event_id: int,
        stars_count: int,
        comment: str | None,
    ) -> Review:
        review = Review(
            user_id=user_id,
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