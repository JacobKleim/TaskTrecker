"""
Модуль task_service.

Содержит функции бизнес-логики для создания, обновления,
удаления и получения задач.

Работает напрямую с базой данных через SQLAlchemy ORM.
"""

import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Task
from app.exceptions import ForbiddenTaskDeleteException, ForbiddenTaskUpdateException, TaskNotFoundException
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.schemas.user import UserRead


logger = logging.getLogger(__name__)


class TaskService:
    """
    Сервис для работы с задачами.

    Выполняет всю бизнес-логику: проверку прав доступа, обработку ошибок, управление транзакциями.
    """

    @staticmethod
    async def create_task(
        task_data: TaskCreate, db: AsyncSession, user: UserRead
    ) -> TaskRead:
        """
        Создаёт новую задачу и сохраняет её в базе данных.

        Args:
            task_data (TaskCreate): Данные, необходимые для создания задачи.
            db (AsyncSession): Асинхронная сессия базы данных.
            user (UserRead): Текущий аутентифицированный пользователь.

        Returns:
            TaskRead: Представление созданной задачи.
        """
        task = Task(
            title=task_data.title, description=task_data.description, user_id=user.id
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def get_task(task_id: int, db: AsyncSession, user: UserRead) -> TaskRead:
        """
        Получает задачу по ID, проверяя принадлежность текущему пользователю.

        Args:
            task_id (int): Идентификатор задачи.
            db (AsyncSession): Асинхронная сессия базы данных.
            user (UserRead): Текущий пользователь, которому должна принадлежать задача.

        Returns:
            TaskRead: Найденная задача.

        Raises:
            TaskNotFoundException: 404, если задача не найдена.
        """
        result = await db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user.id)
        )
        task = result.scalar_one_or_none()
        if task is None:
            raise TaskNotFoundException()
        return task

    @staticmethod
    async def get_all_tasks(db: AsyncSession) -> List[TaskRead]:
        """
        Получает список всех задач в базе данных.

        Args:
            db (AsyncSession): Асинхронная сессия базы данных.

        Returns:
            List[TaskRead]: Список всех задач.
        """
        result = await db.execute(select(Task))
        return result.scalars().all()

    @staticmethod
    async def update_task(
        task_id: int, task_data: TaskUpdate, db: AsyncSession, user: UserRead
    ) -> TaskRead:
        """
        Обновляет задачу, если она существует и принадлежит текущему пользователю.

        Args:
            task_id (int): Идентификатор обновляемой задачи.
            task_data (TaskUpdate): Новые данные задачи.
            db (AsyncSession): Асинхронная сессия базы данных.
            user (UserRead): Текущий пользователь.

        Returns:
            TaskRead: Обновлённая задача.

        Raises:
            TaskNotFoundException: 404, если задача не найдена.
            ForbiddenTaskUpdateException: 403, если нет прав на изменение.
        """
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if task is None:
            TaskNotFoundException()
        if task.user_id != user.id:
            raise ForbiddenTaskUpdateException()
        task.title = task_data.title
        task.description = task_data.description
        task.completed = task_data.completed
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def delete_task(task_id: int, db: AsyncSession, user: UserRead) -> None:
        """
        Удаляет задачу по ID, если она принадлежит текущему пользователю.

        Args:
            task_id (int): Идентификатор задачи.
            db (AsyncSession): Асинхронная сессия базы данных.
            user (UserRead): Текущий пользователь.

        Raises:
            TaskNotFoundException: 404, если задача не найдена.
            ForbiddenTaskDeleteException: 403, если нет прав на удаление.
        """
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if task is None:
            raise TaskNotFoundException()
        if task.user_id != user.id:
            raise ForbiddenTaskDeleteException()
        await db.delete(task)
        await db.commit()
