from fastapi import APIRouter, Query, status

from app.core.dependencies import DbSession, CurrentAdmin
from app.schemas.category import CategoryResponse, CategoryCreate
from app.schemas.pagination import Page, Pagination
from app.services.category import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])
admin_router = APIRouter(prefix="/admin/categories", tags=["categories", "admin"])


@router.get("/", response_model=Page[CategoryResponse])
async def list_categories(
    db: DbSession,
    pagination: Pagination,
    search: str | None = Query(None, min_length=1, max_length=50),
):
    return await CategoryService(db).list_categories(search=search, pagination=pagination)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: DbSession):
    return await CategoryService(db).get_category(category_id=category_id)

######### Admin routes ###############

@admin_router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, current_admin: CurrentAdmin, db: DbSession):
    return await CategoryService(db).create(data=data)