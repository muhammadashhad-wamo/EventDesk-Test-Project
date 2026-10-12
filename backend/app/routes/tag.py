from fastapi import APIRouter

from app.core.dependencies import DbSession
from app.schemas.tag import TagResponse
from app.services.tag import TagService

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: int, db: DbSession):
    return await TagService(db).get_tag(tag_id=tag_id)