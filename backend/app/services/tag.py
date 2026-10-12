from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.tag import TagRepository
from app.schemas.tag import TagResponse


class TagService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.tags = TagRepository(db)
    async def get_tag(self, *, tag_id: int) -> TagResponse:
        tag = await self.tags.get_by_id(tag_id)
        if tag is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Tag not found")
        return TagResponse.model_validate(tag)