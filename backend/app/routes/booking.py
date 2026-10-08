from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.booking import BookingResponse, BookingCreate
from app.services.booking import BookingService

router = APIRouter(tags=["bookings"])


@router.get("/bookings/me", response_model=list[BookingResponse])
async def get_my_bookings(user: CurrentUser, db: DbSession):
    return await BookingService(db).get_my_bookings(user_id=user.id)

@router.post(
    "/events/{event_id}/bookings",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def book_tickets(event_id: int, data: BookingCreate, user: CurrentUser, db: DbSession):
    return await BookingService(db).book(user_id=user.id, event_id=event_id, data=data)