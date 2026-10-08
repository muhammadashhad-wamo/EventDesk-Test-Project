from fastapi import APIRouter, status

from app.core.dependencies import DbSession, GetViewableEvent, CurrentUser, GetEditableReview
from app.schemas.review import (
    ReviewResponse,
    ReviewCreate,
    ReviewUpdate
)
from app.services.review import ReviewService

router = APIRouter(tags=["reviews"])


@router.get("/events/{event_id}/reviews", response_model=list[ReviewResponse])
async def get_event_reviews(event: GetViewableEvent, db: DbSession):
    return await ReviewService(db).get_event_reviews(event_id=event.id)

@router.post(
    "/events/{event_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(event_id: int, data: ReviewCreate, user: CurrentUser, db: DbSession):
    return await ReviewService(db).create(user=user, event_id=event_id, data=data)

@router.patch("/reviews/{review_id}", response_model=ReviewResponse)
async def edit_review(review: GetEditableReview, data: ReviewUpdate, user: CurrentUser, db: DbSession):
    return await ReviewService(db).update(user=user, review=review, data=data)

@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(review_id: int, review: GetEditableReview, db: DbSession):
    await ReviewService(db).delete(review_id=review_id)