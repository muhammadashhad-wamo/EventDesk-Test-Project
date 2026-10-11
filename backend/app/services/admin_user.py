from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AuditAction, AuditEntity, UserRole
from app.repositories.audit_log import AuditLogRepository
from app.repositories.user import UserRepository
from app.schemas.admin_user import AdminUserResponse
from app.schemas.user import UserBase
from app.schemas.pagination import Page, PaginationParams


class AdminUserService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.users = UserRepository(db)
        self.audit = AuditLogRepository(db)

    async def list_users(
        self,
        *,
        pagination: PaginationParams,
        search: str | None,
        role: UserRole | None,
        is_active: bool | None,
    ) -> Page[AdminUserResponse]:
        db_users, total = await self.users.search(
            search=search,
            role=role,
            is_active=is_active,
            limit=pagination.limit,
            offset=pagination.offset,
        )
        return Page[AdminUserResponse](
            items=[AdminUserResponse.model_validate(u) for u in db_users],
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
        )

    async def change_role(self, *, actor: UserBase, user_id: int, role: UserRole) -> AdminUserResponse:
        if user_id == actor.id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Admins cannot change their own role")

        user = await self.users.get_by_id(user_id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

        if UserRole(user.role) == role:
            raise HTTPException(status.HTTP_409_CONFLICT, f"User already has role '{role.value}'")

        try:
            user = await self.users.set_role(user=user, role=role)
            await self.audit.create(
                actor_id=actor.id,
                action=AuditAction.USER_ROLE_CHANGED,
                entity_type=AuditEntity.USER,
                entity_id=user.id,
            )
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

        return AdminUserResponse.model_validate(user)