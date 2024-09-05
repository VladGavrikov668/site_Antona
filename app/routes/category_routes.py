from typing import List
from ..database.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from ..schemas.schemas import CategoryResponse, CategoryCreate, CategoryDelete
from ..sessions.sessions_category import create_category, get_by_name, get_category_all, delete_category

router = APIRouter()


@router.get("/categories", response_model=List[CategoryResponse], tags=["Категории"])
async def get_all_categories(db: AsyncSession = Depends(get_db)):
    try:
        result = await get_category_all(db)
        if result is None:
            raise HTTPException(status_code=404, detail="Категория не найдена")
        return result
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при получении категорий")


@router.get("/categories/{name}", response_model=CategoryResponse, tags=["Категории"])
async def get_categories_by_name(name: str, db: AsyncSession = Depends(get_db)):
    category = await get_by_name(db, name)
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return category


@router.post("/categories/add", response_model=CategoryCreate, tags=["Категории"])
async def add_categories(category_create: CategoryCreate, db: AsyncSession = Depends(get_db)):
    existing_category = await get_by_name(db, category_create.name)
    if existing_category:
        raise HTTPException(status_code=400, detail="Такая категория уже существует!")

    new_category = await create_category(db, category_create)
    return new_category


@router.delete("/categories/{name}", response_model=CategoryDelete, tags=["Категории"])
async def delete_categories_by_name(name: str, db: AsyncSession = Depends(get_db)):
    delete_name = await delete_category(db, name)
    return delete_name
