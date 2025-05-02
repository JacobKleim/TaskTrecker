import asyncio

import pytest_asyncio
from fastapi_users.password import PasswordHelper
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.db.database import get_async_session
from app.api.db.models import User
from app.main import app


USER_TRUE_EMAIL = "test@example.com"
USER_TRUE_PASSWORD = "strongpassword123"
USER_TRUE_USERNAME = "test_user"
USER_TRUE_HASHED_PASSWORD = PasswordHelper().hash(USER_TRUE_PASSWORD)

NEW_USER_EMAIL = "new_test@example.com"

USER_FALSE_EMAIL = "test.false@example.com"
USER_FALSE_PASSWORD = "strongpassword123false"
USER_FALSE_USERNAME = "test_users_false"
USER_FALSE_HASHED_PASSWORD = PasswordHelper().hash(USER_FALSE_PASSWORD)


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Event loop на сессию pytest'а"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
async def db_session():
    """Асинхронная БД сессия"""
    async for session in get_async_session():
        yield session


@pytest_asyncio.fixture
async def async_client():
    """Асинхронный клиент для тестов."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture()
async def create_user(
    db_session: AsyncSession,
):
    """Создание тестового пользователя."""

    async def _create(email: str, username: str, password: str) -> User:
        hashed_password = PasswordHelper().hash(password)
        user = User(email=email, username=username, hashed_password=hashed_password)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return _create


@pytest_asyncio.fixture()
async def auth_header(
    async_client: AsyncClient,
):
    """Аутентификация тестового пользователя."""

    async def _get_auth_header(email: str, password: str) -> dict:
        response = await async_client.post(
            "/auth/jwt/login",
            data={"username": email, "password": password},
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _get_auth_header


@pytest_asyncio.fixture(autouse=True)
async def clear_test_users(db_session: AsyncSession):
    """Удаление тестовых пользователей перед и после тестов."""
    yield

    await db_session.rollback()
    await db_session.execute(
        text("DELETE FROM users WHERE email IN (:email1, :email2, :email3)"),
        {
            "email1": USER_FALSE_EMAIL,
            "email2": USER_TRUE_EMAIL,
            "email3": NEW_USER_EMAIL,
        },
    )
    await db_session.commit()
