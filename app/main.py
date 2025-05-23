"""
Точка входа в приложение FastAPI.

Инициализирует экземпляр FastAPI, подключает роутеры пользователей, задач
и авторизации через FastAPI Users с использованием JWT-аутентификации.
"""

from fastapi import FastAPI

from app.api import tasks, users
from app.core.auth_settings import auth_backend, fastapi_users
from app.core.logging_config import setup_logging
from app.monitoring.metrics import metrics_router, prometheus_middleware

setup_logging()

app = FastAPI()


app.middleware("http")(prometheus_middleware)

app.include_router(metrics_router)
app.include_router(users.router, tags=["users"])
app.include_router(tasks.router, tags=["tasks"])
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
