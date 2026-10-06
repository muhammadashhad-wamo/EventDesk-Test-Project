from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser
from app.schemas.user import UserResponse, UserUpdate

from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser):
    return current_user

@router.patch("/me", response_model=UserResponse)
async def create_user(data: UserUpdate, current_user: CurrentUser):
    return await UserService.update(
        data=data,
        user=current_user
    )

@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_current_user(
    current_user: CurrentUser
):
    await UserService.delete(current_user)