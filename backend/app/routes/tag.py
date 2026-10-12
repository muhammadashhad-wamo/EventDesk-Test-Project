from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.schemas.tag import TagResponse
from app.services.tag import TagService

from app.schemas.pagination import Pagination, Page

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: int, db: DbSession):
    return await TagService(db).get_tag(tag_id=tag_id)

@router.get("/", response_model=Page[TagResponse])
async def list_tags(
    db: DbSession,
    pagination: Pagination,
    search: str | None = Query(None, min_length=1, max_length=50),
):
    return await TagService(db).list_tags(search=search, pagination=pagination)