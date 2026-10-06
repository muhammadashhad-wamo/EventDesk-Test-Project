from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser
from app.schemas.user import UserResponse, UserUpdate, ChangePasswordRequest

from app.services.user import UserService

from app.core.dependencies import DbSession

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser):
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_user(data: UserUpdate, current_user: CurrentUser, db: DbSession):
    return await UserService(db).update(
        data=data,
        user=current_user
    )

@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_current_user(
    current_user: CurrentUser,
    db: DbSession
):
    await UserService(db).delete(user=current_user)

@router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(data: ChangePasswordRequest, current_user: CurrentUser, db: DbSession):
    await UserService(db).update_password(user=current_user, data=data)