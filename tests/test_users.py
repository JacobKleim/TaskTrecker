"""
Тесты для эндпоинтов пользователей в FastAPI.

Этот файл содержит тесты для проверки работы API пользователей,
включая регистрацию, аутентификацию, получение данных о пользователе,
обновление и удаление пользователей.
Используются асинхронные фикстуры для создания пользователей,
аутентификации и взаимодействия с базой данных.

Каждый тест проверяет:
- Корректность кода ответа.
- Ожидаемое поведение эндпоинтов при различных сценариях (успешный запрос, ошибка, неверные права доступа).
"""

import logging

import pytest
from conftest import (
    USER_FALSE_EMAIL,
    USER_FALSE_PASSWORD,
    USER_FALSE_USERNAME,
    USER_TRUE_EMAIL,
    USER_TRUE_PASSWORD,
    USER_TRUE_USERNAME,
)
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User

logger = logging.getLogger(__name__)

NEW_EMAIL = "new_test@example.com"
NEW_USERNAME = "new_test_user"


@pytest.mark.asyncio
async def test_register_user(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Тест регистрации нового пользователя."""

    payload = {
        "email": USER_TRUE_EMAIL,
        "password": USER_TRUE_PASSWORD,
        "username": USER_TRUE_USERNAME,
    }

    response = await async_client.post("/users", json=payload)
    assert response.status_code == 201

    data = response.json()
    user_in_db = await db_session.get(User, data["id"])

    assert user_in_db is not None
    assert user_in_db.id == data["id"]
    assert user_in_db.email == data["email"]
    assert data["username"] == data["username"]


@pytest.mark.asyncio
async def test_login_user(async_client: AsyncClient, create_user) -> None:
    """Тест аутентификации пользователя."""

    await create_user(
        username=USER_TRUE_USERNAME, email=USER_TRUE_EMAIL, password=USER_TRUE_PASSWORD
    )
    response = await async_client.post(
        "/auth/jwt/login",
        data={"username": USER_TRUE_EMAIL, "password": USER_TRUE_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_user(async_client: AsyncClient, create_user) -> None:
    """Тест получения пользователя по ID."""
    user = await create_user(
        username=USER_TRUE_USERNAME, email=USER_TRUE_EMAIL, password=USER_TRUE_PASSWORD
    )

    response = await async_client.get(f"/users/{user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.id
    assert data["email"] == USER_TRUE_EMAIL
    assert data["username"] == USER_TRUE_USERNAME


@pytest.mark.asyncio
async def test_get_all_users(async_client: AsyncClient, create_user) -> None:
    """Тест получения всех пользователей."""
    await create_user(
        email=USER_TRUE_EMAIL, username=USER_TRUE_USERNAME, password=USER_TRUE_PASSWORD
    )
    await create_user(
        email=USER_FALSE_EMAIL,
        username=USER_FALSE_USERNAME,
        password=USER_FALSE_PASSWORD,
    )

    response = await async_client.get("/users")
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert any(u["email"] == "test@example.com" for u in data)
    assert any(u["email"] == "test.false@example.com" for u in data)


@pytest.mark.asyncio
async def test_update_user(async_client: AsyncClient, create_user, auth_header) -> None:
    """Тест обновления пользователя."""
    true_user = await create_user(
        USER_TRUE_EMAIL, USER_TRUE_USERNAME, USER_TRUE_PASSWORD
    )
    true_header = await auth_header(USER_TRUE_EMAIL, USER_TRUE_PASSWORD)

    _ = await create_user(USER_FALSE_EMAIL, USER_FALSE_USERNAME, USER_FALSE_PASSWORD)
    false_header = await auth_header(USER_FALSE_EMAIL, USER_FALSE_PASSWORD)

    payload = {"email": NEW_EMAIL, "username": NEW_USERNAME}
    response = await async_client.put(
        f"/users/{true_user.id}", json=payload, headers=true_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == NEW_EMAIL
    assert data["username"] == NEW_USERNAME

    response_with_false_header = await async_client.put(
        f"/users/{true_user.id}", json=payload, headers=false_header
    )
    assert response_with_false_header.status_code == 403


@pytest.mark.asyncio
async def test_delete_user(async_client: AsyncClient, create_user, auth_header) -> None:
    """Тест удаления пользователя."""
    true_user = await create_user(
        USER_TRUE_EMAIL, USER_TRUE_USERNAME, USER_TRUE_PASSWORD
    )
    true_header = await auth_header(USER_TRUE_EMAIL, USER_TRUE_PASSWORD)

    _ = await create_user(USER_FALSE_EMAIL, USER_FALSE_USERNAME, USER_FALSE_PASSWORD)
    false_header = await auth_header(USER_FALSE_EMAIL, USER_FALSE_PASSWORD)

    response_with_false_header = await async_client.delete(
        f"/users/{true_user.id}", headers=false_header
    )
    assert response_with_false_header.status_code == 403

    response = await async_client.delete(f"/users/{true_user.id}", headers=true_header)
    assert response.status_code == 204 or response.status_code == 200

    response_check = await async_client.get(f"/users/{true_user.id}")
    assert response_check.status_code == 404
