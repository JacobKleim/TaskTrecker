"""
Точка входа в приложение FastAPI.

Инициализирует экземпляр FastAPI, подключает роутеры пользователей, задач
и авторизации через FastAPI Users с использованием JWT-аутентификации.
"""

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import tasks, users
from app.core.auth_settings import auth_backend, fastapi_users
from app.core.logging_config import setup_logging

setup_logging()

app = FastAPI()

Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    excluded_handlers=["/metrics", "/docs", "/openapi.json"],
).instrument(app).expose(app)


app.include_router(users.router, tags=["users"])
app.include_router(tasks.router, tags=["tasks"])
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
