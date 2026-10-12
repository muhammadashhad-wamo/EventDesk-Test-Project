from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag, event_tag


class TagRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, tag_id: int) -> Tag | None:
        return await self.db.get(Tag, tag_id)

    async def search(
        self,
        *,
        search: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Tag], int]:
        conditions = []
        if search:
            conditions.append(Tag.tag.icontains(search, autoescape=True))

        statement = select(Tag).where(*conditions).order_by(Tag.tag).limit(limit).offset(offset)
        tags = await self.db.scalars(statement)
        total = await self.db.scalar(select(func.count(Tag.id)).where(*conditions))
        return tags.all(), total or 0