from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User as User
from app.repositories.user import UserRepository
from app.schemas.user import UserUpdate, UserResponse, UserBase, ChangePasswordRequest
from app.core.security import verify_password, hash_password

from app.core.enums import UserRole


class UserService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.users = UserRepository(db)

    async def update(self, *, data: UserUpdate, user: UserUpdate) -> UserResponse:
        update_data = data.model_dump(exclude_unset=True)

        db_user = User(**user.model_dump())

        new_user = await self.users.update(
            data=update_data,
            user=db_user
        )

        await self._db.commit()
        return new_user

    async def delete(self, *, user: UserBase) -> None:
        db_user = User(**user.model_dump())
        await self.users.delete(user=db_user)
        await self._db.commit()

    async def update_password(self, *, data: ChangePasswordRequest, user: UserBase) -> None:
        if not verify_password(plain_password=data.current_password.get_secret_value(), hashed_password=user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        new_password_hash = data.new_password.get_secret_value()

        db_user = User(**user.model_dump())
        await self.users.update_password(user=db_user, new_password_hash=new_password_hash)
        await self._db.commit()