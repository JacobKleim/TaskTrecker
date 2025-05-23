"""
Модуль user_service.

Содержит функции бизнес-логики для создания, обновления,
удаления и получения задач.

Работает напрямую с базой данных через SQLAlchemy ORM.
"""

import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.exceptions import (
    ForbiddenUserDeleteException,
    ForbiddenUserUpdateException,
    UserNotFoundException,
)
from app.schemas.user import UserRead, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """
    Сервисный слой для работы с пользователями.

    Содержит методы получения, обновления и удаления пользователей с
    проверкой прав доступа и работы с асинхронной сессией SQLAlchemy.
    """

    @staticmethod
    async def get_user_by_id(user_id: int, db: AsyncSession) -> UserRead:
        """
        Получить пользователя по его ID.

        Args:
            user_id (int): Идентификатор пользователя.
            db (AsyncSession): Асинхронная сессия базы данных.

        Returns:
            UserRead: Объект пользователя.

        Raises:
            UserNotFoundException: 404, если пользователь не найден.
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundException()
        return user

    @staticmethod
    async def get_all_users(db: AsyncSession) -> List[UserRead]:
        """
        Получить всех пользователей из базы данных.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных.

        Returns:
            List[UserRead]: Список всех пользователей.
        """
        result = await db.execute(select(User))
        return result.scalars().all()

    @staticmethod
    async def update_user(
        user_id: int, update_data: UserUpdate, db: AsyncSession, current_user: UserRead
    ) -> UserRead:
        """
        Обновить данные пользователя, если текущий пользователь — владелец.

        Args:
            user_id (int): Идентификатор пользователя, которого нужно обновить.
            update_data (UserUpdate): Новые данные пользователя.
            db (AsyncSession): Асинхронная сессия базы данных.
            current_user (UserRead): Пользователь, выполняющий операцию.

        Returns:
            UserRead: Обновлённый пользователь.

        Raises:
            ForbiddenUserUpdateException: 403, если попытка обновить чужого пользователя.
            UserNotFoundException: 404, если пользователь не найден.
        """
        if current_user.id != user_id:
            raise ForbiddenUserUpdateException()
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundException()
        user.email = update_data.email
        user.username = update_data.username
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete_user(
        user_id: int, db: AsyncSession, current_user: UserRead
    ) -> None:
        """
        Удалить пользователя по ID, если он является текущим пользователем.

        Args:
            user_id (int): Идентификатор удаляемого пользователя.
            db (AsyncSession): Асинхронная сессия базы данных.
            current_user (UserRead): Пользователь, выполняющий удаление.

        Raises:
            ForbiddenUserDeleteException: 403, если попытка удалить чужого пользователя.
            UserNotFoundException: 404, если пользователь не найден.
        """
        if current_user.id != user_id:
            raise ForbiddenUserDeleteException()
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundException()
        await db.delete(user)
        await db.commit()
