from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryResponse, CategoryCreate
from app.schemas.pagination import Page, PaginationParams


class CategoryService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self.categories = CategoryRepository(db)

    async def get_category(self, *, category_id: int) -> CategoryResponse:
        category = await self.categories.get_by_id(category_id)
        if category is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
        return CategoryResponse.model_validate(category)

    async def list_categories(
        self, *, search: str | None, pagination: PaginationParams
    ) -> Page[CategoryResponse]:
        db_categories, total = await self.categories.search(
            search=search, limit=pagination.limit, offset=pagination.offset
        )
        return Page[CategoryResponse](
            items=[CategoryResponse.model_validate(c) for c in db_categories],
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
        )

    async def create(self, *, data: CategoryCreate) -> CategoryResponse:
        if await self.categories.get_by_name(data.name) is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "Category already exists")

        try:
            category = await self.categories.create(name=data.name)
            await self._db.commit()
        except IntegrityError:
            await self._db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Category already exists")
        except Exception:
            await self._db.rollback()
            raise

        return CategoryResponse.model_validate(category)