from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserUpdate

from app.core.enums import UserRole

from backend.app.db.session import User


class UserService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.users = UserRepository(db)

    async def update(self, *, data: UserUpdate, user: User) -> User:
        update_data = data.model_dump(exclude_unset=True)

        new_user = await self.users.update(
            data=update_data,
            user=user
        )

        self._db.commit()
        return new_user

    async def delete(self, *, user: User) -> User:
        await self.user_repository.delete(user)