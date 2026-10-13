from typing import Annotated
from fastapi import APIRouter, status, Query

from app.schemas.user import UserResponse, UserUpdate, ChangePasswordRequest, UserLookupResponse
from app.schemas.admin_user import RoleUpdate, AdminUserResponse

from app.services.user import UserService
from app.services.admin_user import AdminUserService

from app.core.dependencies import CurrentUser, CurrentAdmin
from app.core.dependencies import DbSession

from app.schemas.pagination import Page, Pagination

from app.core.enums import UserRole

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

@router.get("/lookup", response_model=list[UserLookupResponse])
async def lookup_users(
    user: CurrentUser,
    db: DbSession,
    search: Annotated[str, Query(min_length=2, max_length=50)],
    limit: int = Query(10, ge=1, le=20),
):
    return await UserService(db).search_active_by_name(search=search, limit=limit)


############## Admin routes ##################
@admin_router.get("", response_model=Page[AdminUserResponse])
async def list_users(
    current_admin: CurrentAdmin,
    db: DbSession,
    pagination: Pagination,
    search: str | None = Query(None, min_length=1, max_length=100, description="Matches name or email"),
    role: UserRole | None = None,
    is_active: bool | None = None,
):
    return await AdminUserService(db).list_users(
        pagination=pagination, search=search, role=role, is_active=is_active
    )

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
async def delete_user_by_id(user_id: int, current_admin: CurrentAdmin, db: DbSession):
    await UserService(db).delete_by_id(id=user_id, actor_id=current_admin.id)

@admin_router.patch("/{user_id}/role", response_model=AdminUserResponse)
async def change_user_role(user_id: int, data: RoleUpdate, current_admin: CurrentAdmin, db: DbSession):
    return await AdminUserService(db).change_role(actor=current_admin, user_id=user_id, role=data.role)