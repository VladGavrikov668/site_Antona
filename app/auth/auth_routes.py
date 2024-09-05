from fastapi import Depends, APIRouter, Query, HTTPException
from fastapi.params import Body
from fastapi_users import FastAPIUsers, fastapi_users
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse

from .auth import auth_backend
from .database_auth import User
from .manager import get_user_manager, UserManager
from .schemas_auth import UserRead, UserCreate
from ..database.database import get_db
from .tasks import send_verification_email, send_password

router = APIRouter()

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["Авторизация"],
)

current_user = fastapi_users.current_user()


@router.post("/register", tags=["Авторизация"])
async def register(user_create: UserCreate, session: AsyncSession = Depends(get_db)):
    user_manager = await get_user_manager(session)
    user = await user_manager.create(user_create, safe=True)
    verification_link = f"http://localhost:8000/verify-email?token={user.email}"
    send_verification_email.delay(user.email, verification_link)
    return {"message": "Пожалуйста, проверьте вашу почту для подтверждения аккаунта"}


@router.get("/verify-email", tags=["Авторизация"])
async def verify_email(token: str = Query(...), user_manager: UserManager = Depends(get_user_manager)):
    try:
        await user_manager.verify_user(token)
        return {"message": "Thanks, bro. Your is good!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/protected-route", tags=["Авторизация"])
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.username}"


@router.get("/unprotected-route", tags=["Авторизация"])
def unprotected_route():
    return f"Hello, anonym"


@router.get("/forgot-password", response_class=RedirectResponse, tags=["Сброс пароля"])
async def forgot_password():
    return RedirectResponse(url="/reset-password")


@router.post("/reset-password", tags=["Сброс пароля"])
async def reset_password_request(email: str = Body(..., embed=True),
                                 user_manager: UserManager = Depends(get_user_manager)):
    try:
        user = await user_manager.get_by_email(email)
        if user is None:
            raise HTTPException(status_code=404, detail="Пользователь с таким email не найден")

        reset_token = await user_manager.forgot_password(user)
        reset_link = f"http://localhost:8000/auth/confirm-reset-password?token={reset_token}"
        send_password.delay(user.email, reset_link)

        return {"message": "Ссылка для сброса пароля отправлена на вашу почту."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/confirm-reset-password", tags=["Сброс пароля"])
async def confirm_reset_password(token: str = Query(...), new_password: str = Body(..., embed=True),
                                 user_manager: UserManager = Depends(get_user_manager)):
    try:
        await user_manager.reset_password(token, new_password)
        return {"message": "Пароль успешно изменен."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
