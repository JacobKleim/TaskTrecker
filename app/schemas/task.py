"""
Pydentic модели для валидации данных задачи(task).
"""

import logging
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class TaskBase(BaseModel):
    """Базовая схема задачи с общими полями."""

    title: str = Field(min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    completed: bool = False

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(TaskBase):
    """Схема для создания задачи."""

    pass


class TaskUpdate(TaskBase):
    """Схема для обновления задачи."""

    pass


class TaskRead(TaskBase):
    """Схема для чтения задачи, включая ID и user_id."""

    user_id: int
    id: int
