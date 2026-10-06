from fastapi import APIRouter, status

from app.schemas.user import UserResponse, UserUpdate, ChangePasswordRequest

from app.services.user import UserService

from app.core.dependencies import CurrentUser, CurrentAdmin
from app.core.dependencies import DbSession

user_router = APIRouter(prefix="/users", tags=["users"])
admin_router = APIRouter(prefix="/admin/users", tags=["admin", "users"])

@user_router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser):
    return current_user

@user_router.patch("/me", response_model=UserResponse)
async def update_user(data: UserUpdate, current_user: CurrentUser, db: DbSession):
    return await UserService(db).update(
        data=data,
        user=current_user
    )

@user_router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_current_user(
    current_user: CurrentUser,
    db: DbSession
):
    await UserService(db).delete(user=current_user)

@user_router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(data: ChangePasswordRequest, current_user: CurrentUser, db: DbSession):
    await UserService(db).update_password(user=current_user, data=data)


############## Admin routes ##################
@admin_router.get("/", response_model=list[UserResponse])
async def get_users(current_admin: CurrentAdmin, db: DbSession):
    return await UserService(db).get_users()