"""
Маршруты API для пользователей (users).

Вызывают методы из слоя сервисов.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends
from fastapi_users.manager import BaseUserManager
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_tasks.notifications import send_email
from app.core.auth_settings import fastapi_users, get_user_manager
from app.db.database import get_async_session
from app.db.models import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

get_current_user = fastapi_users.current_user()
router = APIRouter()


@router.post("/users", status_code=201, response_model=UserRead)
async def register(
    user: UserCreate,
    user_manager: BaseUserManager[User, int] = Depends(get_user_manager),
) -> UserRead:
    """Создание пользователя."""
    user = await user_manager.create(user)
    send_email.delay(to_email=user.email, subject="Регистрация", body='Ваша учетная запись успешно создана')
    return user


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> UserRead:
    """Получение информации о пользователе."""
    return await UserService.get_user_by_id(user_id, db)


@router.get("/users", response_model=List[UserRead])
async def get_all_users(
    db: AsyncSession = Depends(get_async_session),
) -> List[UserRead]:
    """Получение всех пользователей."""
    return await UserService.get_all_users(db)


@router.put("/users/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserRead = Depends(get_current_user),
) -> UserRead:
    """Обновление информации о пользователе."""
    return await UserService.update_user(user_id, user_update, db, current_user)


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserRead = Depends(get_current_user),
) -> None:
    """Удаление пользователя."""
    await UserService.delete_user(user_id, db, current_user)
