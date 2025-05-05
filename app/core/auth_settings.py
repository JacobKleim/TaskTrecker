"""
Модуль настройки аутентификации и управления пользователями с использованием fastapi-users.

Реализует:
- JWT-стратегию на основе конфигурации;
- кастомный UserManager;
- SQLAlchemyUserDatabase;
- AuthenticationBackend для JWT;
- Экземпляр FastAPIUsers, подключённый к менеджеру и backend-стратегии.
"""

import logging
from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.manager import BaseUserManager
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import load_config
from app.db.database import get_async_session
from app.db.models import User


logger = logging.getLogger(__name__)

config = load_config()


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


class UserManager(BaseUserManager[User, int]):
    """
    Менеджер пользователей, реализующий кастомную логику преобразования ID.

    Методы:
        parse_id(str) -> int: Преобразует строковый ID в целочисленный.
    """

    def parse_id(self, user_id: str) -> int:
        return int(user_id)


async def get_jwt_strategy() -> AsyncGenerator[JWTStrategy, None]:
    """
    Возвращает стратегию JWT на основе конфигурации.

    Returns:
        AsyncGenerator[JWTStrategy, None]: Генератор с JWT-стратегией.
    """
    yield JWTStrategy(
        secret=config.jwt.secret_key,
        lifetime_seconds=config.jwt.access_token_expire_seconds,
    )


async def get_user_db(
    db: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    """
    Возвращает объект SQLAlchemyUserDatabase для работы с пользователями.

    Args:
        db (AsyncSession): Сессия БД, полученная через Depends.

    Returns:
        AsyncGenerator[SQLAlchemyUserDatabase, None]: Генератор с БД пользователей.
    """
    yield SQLAlchemyUserDatabase(db, User)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """
    Возвращает экземпляр кастомного UserManager.

    Args:
        user_db (SQLAlchemyUserDatabase): Объект БД пользователей.

    Returns:
        AsyncGenerator[UserManager, None]: Генератор с менеджером пользователей.
    """
    yield UserManager(user_db)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_backend],
)
