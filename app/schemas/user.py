"""
Pydentic модели для валидации данных пользователя(user).
"""

import logging

from fastapi_users import schemas
from pydantic import ConfigDict, EmailStr, Field

logger = logging.getLogger(__name__)


class UserCreate(schemas.BaseUserCreate):
    """Схема для создания нового пользователя."""

    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    username: str = Field(min_length=3, max_length=50)

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(schemas.BaseUserUpdate):
    """Схема для обновления данных пользователя."""

    username: str = Field(min_length=3, max_length=50)

    model_config = ConfigDict(from_attributes=True)


class UserRead(schemas.BaseUser):
    """Схема для отображения пользователя."""

    id: int
    username: str = Field(min_length=3, max_length=50)

    model_config = ConfigDict(from_attributes=True)
