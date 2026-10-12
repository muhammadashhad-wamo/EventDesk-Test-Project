from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.tag import TagRepository
from app.schemas.tag import TagResponse, TagCreate

from app.schemas.pagination import PaginationParams, Page


class TagService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.tags = TagRepository(db)

    async def get_tag(self, *, tag_id: int) -> TagResponse:
        tag = await self.tags.get_by_id(tag_id)
        if tag is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Tag not found")
        return TagResponse.model_validate(tag)
    
    async def list_tags(self, *, search: str | None, pagination: PaginationParams) -> Page[TagResponse]:
        db_tags, total = await self.tags.search(
            search=search, limit=pagination.limit, offset=pagination.offset
        )
        return Page[TagResponse](
            items=[TagResponse.model_validate(t) for t in db_tags],
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
        )

    async def create(self, *, data: TagCreate) -> TagResponse:
        if await self.tags.get_by_name(data.tag) is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "Tag already exists")

        try:
            tag = await self.tags.create(name=data.tag)
            await self._db.commit()
        except IntegrityError:
            await self._db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Tag already exists")
        except Exception:
            await self._db.rollback()
            raise

        return TagResponse.model_validate(tag)