from typing import List, Optional
from pydantic import BaseModel, validator
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str
class CategoryDelete(BaseModel):
    name: str
class CategoryResponse(BaseModel):
    id: int
    name: str
    articles: List['ArticleResponse'] = []

    class Config:
        orm_mode = True
        from_attributes = True

class ArticleCreate(BaseModel):
    title: str
    description: str
    date: datetime
    category_id: int


class ArticleDelete(BaseModel):
    title: str


class ArticleResponse(BaseModel):
    id: int
    title: str
    description: str
    date: datetime
    category_id: int
    category: Optional[CategoryResponse]

    class Config:
        orm_mode = True
        from_attributes = True

