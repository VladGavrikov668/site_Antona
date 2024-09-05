from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.database import Base, get_db
from ..models.models import User


async def get_user_db(session: AsyncSession = Depends(get_db)) -> SQLAlchemyUserDatabase:
    return SQLAlchemyUserDatabase(session, User)
