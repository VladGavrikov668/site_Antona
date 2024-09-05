from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas
from fastapi_users.jwt import generate_jwt
import os

from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.exceptions import UserNotExists
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.database import Base, get_db
from .tasks import send_verification_email
from .tasks import celery_app
from .database_auth import get_user_db
from ..models.models import User

SECRET = 'MANAGE_KEY'


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def create(
            self,
            user_create: schemas.UC,
            safe: bool = False,
            request: Optional[Request] = None,
    ) -> models.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict['role_id'] = 1
        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    async def verify_user(self, email: str):
        user = await self.user_db.get_by_email(email)
        if not user:
            raise exceptions.UserNotExists()

        user.is_verified = True
        update_dict = {"is_verified": True}
        await self.user_db.update(user, update_dict)

        print(f"User {user.email} has been verified.")

    async def forgot_password(
            self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        if not user.is_active:
            raise exceptions.UserInactive()

        token_data = {
            "sub": str(user.id),
            "password_fgpt": self.password_helper.hash(user.hashed_password),
            "aud": self.reset_password_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.reset_password_token_secret,
            self.reset_password_token_lifetime_seconds,
        )
        await self.on_after_forgot_password(user, token, request)
        return token


async def get_user_manager(session: AsyncSession = Depends(get_db)) -> UserManager:
    user_db = SQLAlchemyUserDatabase(session, User)
    return UserManager(user_db=user_db)
