from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.db.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, *, name: str, email: str, password_hash: str, role: str) -> User:
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def update(self, *, user: User, data: dict) -> User:
        for field, value in data.items():
            setattr(user, field, value)

        self.db.add(user)

        await self.db.flush()

        return user

    async def delete(self, * user: User) -> None:
        await self.db.delete(user)