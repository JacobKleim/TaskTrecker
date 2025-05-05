"""
Pydentic модели для валидации данных задачи(task).
"""

import logging
from typing import Optional

from pydantic import BaseModel, ConfigDict


logger = logging.getLogger(__name__)


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskRead(TaskBase):
    user_id: int
    id: int
