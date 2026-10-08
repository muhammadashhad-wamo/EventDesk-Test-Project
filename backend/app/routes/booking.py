from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.booking import BookingResponse
from app.services.booking import BookingService

router = APIRouter(tags=["bookings"])


@router.get("/bookings/me", response_model=list[BookingResponse])
async def get_my_bookings(user: CurrentUser, db: DbSession):
    return await BookingService(db).get_my_bookings(user_id=user.id)