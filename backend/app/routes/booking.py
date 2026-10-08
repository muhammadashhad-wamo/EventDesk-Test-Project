from fastapi import APIRouter, status

from app.core.dependencies import CurrentAdmin, CurrentUser, DbSession
from app.schemas.booking import BookingResponse, BookingCreate
from app.services.booking import BookingService

router = APIRouter(tags=["bookings"])
admin_router = APIRouter(prefix="/admin", tags=["bookings", "admin"])


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

@router.patch("/events/{event_id}/bookings/me/cancel", response_model=BookingResponse)
async def cancel_my_booking(event_id: int, user: CurrentUser, db: DbSession):
    return await BookingService(db).cancel(user_id=user.id, event_id=event_id)


######### Admin routes ###############

@admin_router.patch(
    "/events/{event_id}/bookings/{user_id}/cancel",
    response_model=BookingResponse,
)
async def admin_cancel_booking(event_id: int, user_id: int, current_admin: CurrentAdmin, db: DbSession):
    return await BookingService(db).cancel(user_id=user_id, event_id=event_id)