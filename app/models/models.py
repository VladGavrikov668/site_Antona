from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, JSON, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from fastapi_users.db import SQLAlchemyBaseUserTable
from ..database.database import Base


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, unique=True, nullable=False)

    articles = relationship('Article', back_populates='category')


class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    category_id = Column(Integer, ForeignKey('categories.id'))

    category = relationship('Category', back_populates='articles')


class Role(Base):
    __tablename__ = 'role'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    permissions: Mapped[dict] = mapped_column(JSON, nullable=False)


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    number_phone: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    registered_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('role.id'))
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
