from typing import Optional, ClassVar
from fastapi_users import schemas
from fastapi_users.schemas import PYDANTIC_V2
from pydantic import ConfigDict, validator, EmailStr, Field
import re


class UserRead(schemas.BaseUser[int]):
    id: int
    email: str
    username: str
    role_id: int
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr = Field(..., description="Введите ваш email")
    username: str = Field(..., description="Введите имя пользователя")
    password: str = Field(..., description="Введите пароль")
    role_id: int
    number_phone: str = Field(..., description="Введите номер телефона в формате +7 (xxx) xxx xx xx")
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False

    phone_pattern: ClassVar[re.Pattern] = re.compile(r"^\+7 \(\d{3}\) \d{3} \d{2} \d{2}$")

    @validator("number_phone")
    def validate_number_phone(cls, value):
        if not cls.phone_pattern.match(value):
            raise ValueError("Phone number must be in the format: +7 (xxx) xxx xx xx")
        return value

    @validator("password")
    def validate_password(cls, value):
        if len(value) < 7:
            raise ValueError("Password must be at least 7 characters long")
        if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise ValueError("Password must contain both letters and numbers")
        return value




