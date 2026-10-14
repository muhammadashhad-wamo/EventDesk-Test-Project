from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.user import User as User
from app.repositories.user import UserRepository
from app.schemas.user import UserUpdate, UserResponse, UserBase, ChangePasswordRequest, UserLookupResponse
from app.core.security import verify_password, hash_password
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.audit_log import AuditLogRepository
from datetime import datetime, timezone

from app.core.enums import AuditAction, AuditEntity


class UserService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.users = UserRepository(db)
        self.tokens = RefreshTokenRepository(db)
        self.audit = AuditLogRepository(db)

    async def get_by_id(self, id: int) -> UserResponse:
        db_user = await self.users.get_by_id(user_id=id)

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponse.model_validate(db_user)

    async def update_by_id(self, id: int, data: UserUpdate, actor_id: int) -> UserResponse:
        db_user = await self.users.get_by_id(user_id=id)
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        if "email" in update_data:
            update_data["email"] = update_data["email"].lower()
            db_email_user = await self.users.get_by_email(update_data.get("email"))
            if db_email_user and db_email_user.id != id:
                raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="The given email is already associated with an account"
                    )

        new_user = await self.users.update(
            data=update_data,
            user=db_user
        )

        await self.audit.create(
            actor_id=actor_id,
            action=AuditAction.USER_UPDATED,
            entity_type=AuditEntity.USER,
            entity_id=db_user.id
        )

        await self._db.commit()
        return UserResponse.model_validate(new_user)
        

    async def update(self, *, data: UserUpdate, user: UserBase) -> UserResponse:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        if "email" in update_data:
            update_data["email"] = update_data["email"].lower()
            db_email_user = await self.users.get_by_email(update_data.get("email"))
            if db_email_user and db_email_user.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The given email is already associated with an account"
                )

        db_user = await self.users.get_by_id(user_id=id)
                
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        new_user = await self.users.update(
            data=update_data,
            db_user=db_user
        )
        try:
            await self._db.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            await self._db.rollback()
        return UserResponse.model_validate(new_user)

    async def delete_by_id(self, *, id: int, actor_id: int | None = None) -> None:
        if actor_id is not None and id == actor_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The given email is already associated with an account"
            )

        db_user = await self.users.get_by_id(user_id=id)
                
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if db_user.is_active == False:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already deleted"
            )
        
        await self.users.delete(user=db_user)
        await self.tokens.revoke_all_for_user(
            user_id=db_user.id,
            now=datetime.now(timezone.utc)
        )
        await self.audit.create(
            actor_id=actor_id,
            action=AuditAction.USER_DEACTIVATED,
            entity_type=AuditEntity.USER,
            entity_id=db_user.id
        )
        await self._db.commit()

    async def delete(self, *, user: UserBase) -> None:
        db_user = User(**user.model_dump())
        await self.users.delete(user=db_user)
        await self.tokens.revoke_all_for_user(
            user_id=user.id,
            now=datetime.now(timezone.utc)
        )
        await self.audit.create(
            actor_id=user.id,
            action=AuditAction.USER_DEACTIVATED,
            entity_type=AuditEntity.USER,
            entity_id=db_user.id
        )
        await self._db.commit()

    async def activate_by_id(self, id: int, actor_id: int) -> UserResponse:
        db_user = await self.users.get_by_id(user_id=id)
                
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if db_user.is_active == True:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already active"
            )

        update_data = {"is_active": True}

        new_user = await self.users.update(
            data=update_data,
            user=db_user
        )

        await self.audit.create(
            actor_id=actor_id,
            action=AuditAction.USER_ACTIVATED,
            entity_type=AuditEntity.USER,
            entity_id=db_user.id
        )

        await self._db.commit()
        return UserResponse.model_validate(new_user)

    async def update_password(self, *, data: ChangePasswordRequest, user: UserBase) -> None:
        if not verify_password(plain_password=data.current_password.get_secret_value(), hashed_password=user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        new_password_hash = hash_password(data.new_password.get_secret_value())

        if data.new_password.get_secret_value() == data.current_password.get_secret_value():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="New password cannot be same as current password",
            )

        db_user = User(**user.model_dump())
        await self.users.update_password(user=db_user, new_password_hash=new_password_hash)
        await self.tokens.revoke_all_for_user(
            user_id=user.id,
            now=datetime.now(timezone.utc)
        )
        await self._db.commit()

    async def search_active_by_name(self, *, search: str, limit: int) -> list[UserLookupResponse]:
        db_users = await self.users.search_active_by_name(search=search, limit=limit)
        return [UserLookupResponse.model_validate(u) for u in db_users]