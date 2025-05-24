"""
Конфигурация приложения с использованием dataclasses и environs.

Загружает переменные окружения из .env-файла и предоставляет доступ к конфигурации
для базы данных, JWT и режима отладки через объект `Config`.
"""

import logging
from dataclasses import dataclass

from environs import Env

logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """
    Конфигурация для email рассылок.

    Атрибуты:
        email (str): Почта с которой ведется рассылка.
        email_password (int): Пароль приложения.
    """
    email: str
    email_password: str


@dataclass
class JWTConfig:
    """
    Конфигурация JWT.

    Атрибуты:
        secret_key (str): Секретный ключ для подписи токенов.
        access_token_expire_seconds (int): Время жизни токена доступа в секундах.
    """

    secret_key: str
    access_token_expire_seconds: int


@dataclass
class CeleryConfig:
    """
    Конфигурация Celery.

    Атрибуты:
        broker_url (str): URL брокера сообщений.
        result_backend_url (str): URL хранилища результатов.
    """
    broker_url: str
    result_backend_url: str


@dataclass
class DatabaseConfig:
    """
    Конфигурация базы данных.

    Атрибуты:
        database_url (str): URL подключения к базе данных.
    """

    database_url: str


@dataclass
class Config:
    """
    Общая конфигурация приложения.

    Атрибуты:
        db (DatabaseConfig): Настройки подключения к БД.
        jwt (JWTConfig): Настройки JWT.
        debug (bool): Режим отладки.
    """

    db: DatabaseConfig
    jwt: JWTConfig
    debug: bool
    celery: CeleryConfig
    mailing: EmailConfig


def load_config(path: str = "./.env") -> Config:
    """
    Загружает конфигурацию из .env файла.

    Args:
        path (str): Путь до .env файла (по умолчанию "./.env").

    Returns:
        Config: Объект с полной конфигурацией приложения.
    """
    env = Env()
    env.read_env(path)

    return Config(
        db=DatabaseConfig(database_url=env("DATABASE_URL")),
        jwt=JWTConfig(
            secret_key=env("SECRET_KEY"),
            access_token_expire_seconds=env.int(
                "ACCESS_TOKEN_EXPIRE_SECONDS", default=5000
            ),
        ),
        debug=env.bool("DEBUG", default=False),
        celery=CeleryConfig(
            broker_url=env("CELERY_BROKER_URL"),
            result_backend_url=env("CELERY_RESULT_BACKEND_URL"),
        ),
        mailing=EmailConfig(
            email=env("EMAIL"),
            email_password=env("EMAIL_PASSWORD"),
        )
    )
