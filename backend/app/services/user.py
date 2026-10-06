from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User as User
from app.repositories.user import UserRepository
from app.schemas.user import UserUpdate, UserResponse, UserBase

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

    async def delete(self, *, user: UserBase) -> User:
        db_user = User(**user.model_dump())
        await self.users.delete(user=db_user)
        await self._db.commit()