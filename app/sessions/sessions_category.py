from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.models import Category
from ..schemas.schemas import CategoryCreate, CategoryResponse
from sqlalchemy.orm import selectinload


async def create_category(db: AsyncSession, category: CategoryCreate):
    db_category = Category(**category.dict())
    db.add(db_category)

    await db.commit()
    await db.refresh(db_category)
    return db_category


async def get_by_name(db: AsyncSession, category_name: str):
    result = await db.execute(
        select(Category)
        .options(selectinload(Category.articles))
        .where(Category.name == category_name)
    )
    category = result.scalars().first()
    if category:
        return category
    return False


async def get_category_all(db: AsyncSession):
    result = await db.execute(
        select(Category)
        .options(selectinload(Category.articles))
    )
    categories = result.scalars().all()

    return [CategoryResponse.from_orm(category) for category in categories]


async def delete_category(db: AsyncSession, category_name: str):
    category = await get_by_name(db, category_name)

    if not category:
        raise HTTPException(status_code=404, detail=f"Категория с именем '{category_name}' не найдена.")

    await db.execute(delete(Category).where(Category.name == category_name))
    await db.commit()
    return category
