from typing import List
from ..database.database import get_db
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging
from ..schemas.schemas import ArticleResponse, ArticleCreate, ArticleDelete
from ..sessions.sessions_article import get_article_by_name, create_article, delete_article, get_article_all

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
routers = APIRouter()


@routers.get("/articles", response_model=List[ArticleResponse], tags=["Статьи"])
async def get_all_articles_endpoint(db: AsyncSession = Depends(get_db)):
    try:
        result = await get_article_all(db)
        if not result:
            return []
        return result
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при получении статей")


@routers.get("/articles/{title}", response_model=ArticleResponse, tags=["Статьи"])
async def get_article_by_name_endpoint(title: str, db: AsyncSession = Depends(get_db)):
    article = await get_article_by_name(db, title)
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return article


@routers.post("/articles/add", response_model=ArticleCreate, tags=["Статьи"])
async def add_article(article_create: ArticleCreate, db: AsyncSession = Depends(get_db)):
    try:
        existing_article = await get_article_by_name(db, article_create.title)
        if existing_article:
            raise HTTPException(status_code=400, detail="Статья с таким названием уже существует")

        new_article = await create_article(db, article_create)
        return new_article
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating article: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при создании статьи")


@routers.delete("/articles/{title}", response_model=ArticleDelete, tags=["Статьи"])
async def delete_article_by_title(title: str, db: AsyncSession = Depends(get_db)):
    try:
        delete_result = await delete_article(db, title)
        if not delete_result:
            raise HTTPException(status_code=404, detail="Статья не найдена")
        return delete_result
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при удалении статьи")
