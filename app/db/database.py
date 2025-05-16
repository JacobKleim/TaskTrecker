"""
Настройка асинхронного подключения к базе данных с использованием SQLAlchemy.

- Создаёт асинхронный движок с помощью `create_async_engine`.
- Инициализирует фабрику сессий через `async_sessionmaker`.
- Предоставляет зависимость `get_async_session` для FastAPI,
  возвращающую асинхронную сессию SQLAlchemy.
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import load_config

logger = logging.getLogger(__name__)

config = load_config()

DATABASE_URL = config.db.database_url

engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет асинхронную сессию SQLAlchemy для взаимодействия с БД.

    Используется как зависимость в эндпоинтах FastAPI, чтобы обрабатывать транзакции
    с базой данных через единичный жизненный цикл сессии на каждый запрос.
    """
    async with async_session_maker() as session:
        yield session
