from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.models import Article, Category
from ..schemas.schemas import ArticleCreate, ArticleResponse
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_article(db: AsyncSession, article: ArticleCreate):
    try:
        category_result = await db.execute(select(Category).where(Category.id == article.category_id))
        category = category_result.scalars().first()
        if not category:
            raise HTTPException(status_code=404, detail=f"Категория с id {article.category_id} не найдена.")

        db_article = Article(
            title=article.title,
            description=article.description,
            date=article.date,
            category_id=article.category_id
        )
        db.add(db_article)

        await db.commit()
        await db.refresh(db_article)

        return db_article
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while creating article: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при создании статьи в базе данных")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error while creating article: {str(e)}")
        raise HTTPException(status_code=500, detail="Неожиданная ошибка при создании статьи")


async def get_article_all(db: AsyncSession):
    result = await db.execute(
        select(Article)
        .options(selectinload(Article.category))
    )
    articles = result.scalars().all()

    return [ArticleResponse.from_orm(article) for article in articles]


async def get_article_by_name(db: AsyncSession, article_title: str):
    logger.debug("Выполняем запрос к базе данных...")
    result = await db.execute(
        select(Article)
        .options(selectinload(Article.category))
        .where(Article.title == article_title)
    )
    logger.debug("Запрос выполнен, обрабатываем результат...")
    article = result.scalars().first()
    if article:
        logger.debug(f"Статья найдена: {article.title}")
        return article
    logger.debug("Статья не найдена")
    return False


async def delete_article(db: AsyncSession, article_title: str):
    article = await get_article_by_name(db, article_title)

    if not article:
        raise HTTPException(status_code=404, detail=f"Статья с названием '{article_title}' не найдена.")

    await db.execute(delete(Article).where(Article.title == article_title))
    await db.commit()

    return {"message": f"Статья '{article_title}' успешно удалена"}
