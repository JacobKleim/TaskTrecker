"""
Pydentic модели для валидации данных задачи(task).
"""

import logging
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


logger = logging.getLogger(__name__)


class TaskBase(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    completed: bool = False

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskRead(TaskBase):
    user_id: int
    id: int
