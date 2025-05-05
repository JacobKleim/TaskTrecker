"""
Модели базы данных для пользователей и задач.

Содержит определения таблиц 'users' и 'tasks', включая отношения между ними.
Реализовано с использованием SQLAlchemy ORM и FastAPI Users.
"""

import logging
from typing import List, Optional

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""

    pass


class User(Base, SQLAlchemyBaseUserTable):
    """
    Модель пользователя.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя.
        username (str): Отображаемое имя пользователя.
        tasks (List[Task]): Список задач, принадлежащих пользователю.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, index=True)

    tasks: Mapped[List["Task"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Task(Base):
    """
    Модель задачи.

    Атрибуты:
        id (int): Уникальный идентификатор задачи.
        title (str): Название задачи.
        description (Optional[str]): Описание задачи.
        completed (bool): Флаг завершённости задачи.
        user_id (int): Внешний ключ на пользователя (владельца).
        user (User): Отношение к модели пользователя.
    """

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[Optional[str]] = mapped_column(String, index=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(back_populates="tasks")
