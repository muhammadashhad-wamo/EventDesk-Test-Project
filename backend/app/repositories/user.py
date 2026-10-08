from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(self) -> list[User]:
        statement = select(User)
        users = await self.db.scalars(statement)
        return users.all()

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
        # Adding this to eager load required attributes for serialization
        await self.db.refresh(user)
        return user

    async def update(self, *, user: User, data: dict) -> User:
        db_user = await self.db.merge(user)

        for field, value in data.items():
            setattr(db_user, field, value)

        await self.db.flush()

        return db_user

    async def update_password(self, *, user: User, new_password_hash: str) -> None:
        db_user = await self.db.merge(user)
        db_user.password_hash = new_password_hash
        await self.db.flush()

    async def delete(self, *, user: User) -> None:
        db_user = await self.db.merge(user)
        db_user.is_active = False
        await self.db.flush()

    async def get_active_ids(self, user_ids: list[int]) -> list[int]:
        if not user_ids:
            return []
        statement = select(User.id).where(User.id.in_(user_ids), User.is_active == True)
        return list(await self.db.scalars(statement))