from fastapi import APIRouter, status

from app.schemas.user import UserResponse, UserUpdate, ChangePasswordRequest

from app.services.user import UserService

from app.core.dependencies import CurrentUser, CurrentAdmin
from app.core.dependencies import DbSession

router = APIRouter(prefix="/users", tags=["users"])
admin_router = APIRouter(prefix="/admin/users", tags=["admin", "users"])

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


############## Admin routes ##################
@admin_router.get("/", response_model=list[UserResponse])
async def get_users(current_admin: CurrentAdmin, db: DbSession):
    return await UserService(db).get_users()

@admin_router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, current_admin: CurrentAdmin, db: DbSession):
    return await UserService(db).get_by_id(id=user_id)

@admin_router.patch("/{user_id}", response_model=UserResponse)
async def update_user_by_id(user_id: int, data: UserUpdate, current_admin: CurrentAdmin, db: DbSession):
    return await UserService(db).update_by_id(id=user_id, data=data)

@admin_router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate_user_by_id(user_id: int, current_admin: CurrentAdmin, db: DbSession):
    return await UserService(db).activate_by_id(id=user_id)

@admin_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(user_id: int, current_admin: CurrentAdmin, db: DbSession):
    await UserService(db).delete_by_id(id=user_id)