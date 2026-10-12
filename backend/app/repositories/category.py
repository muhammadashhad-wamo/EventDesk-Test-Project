from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.event import Event


class CategoryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, category_id: int) -> Category | None:
        return await self.db.get(Category, category_id)

    async def get_by_name(self, name: str) -> Category | None:
        statement = select(Category).where(
            func.lower(Category.name) == name.strip().lower()
        )
        return await self.db.scalar(statement)

    async def search(
        self, *, search: str | None, limit: int, offset: int
    ) -> tuple[list[Category], int]:
        conditions = []
        if search:
            conditions.append(Category.name.icontains(search, autoescape=True))

        statement = (
            select(Category)
            .where(*conditions)
            .order_by(Category.name, Category.id)
            .limit(limit)
            .offset(offset)
        )
        categories = await self.db.scalars(statement)
        total = await self.db.scalar(select(func.count(Category.id)).where(*conditions))
        return categories.all(), total or 0