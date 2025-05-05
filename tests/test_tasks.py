"""
Тесты для эндпоинтов задач в FastAPI.

Этот файл содержит тесты для проверки работы API задач, включая создание, получение, обновление и удаление задач.
Используются асинхронные фикстуры для создания пользователей, аутентификации и взаимодействия с базой данных.

Каждый тест проверяет:
- Корректность кода ответа.
- Ожидаемое поведение эндпоинтов при различных сценариях (успешный запрос, ошибка, неверные права доступа).
"""

import logging

import pytest
from conftest import (USER_FALSE_EMAIL, USER_FALSE_PASSWORD, USER_FALSE_USERNAME, USER_TRUE_EMAIL, USER_TRUE_PASSWORD,
                      USER_TRUE_USERNAME,)
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Task


logger = logging.getLogger(__name__)

TITLE = "test title"
NEW_TITLE = "new test title"
DESCRIPTION = "test description"
NEW_DESCRIPTION = "new test description"
IS_COMPLETED = False


@pytest.mark.asyncio
async def test_create_task(
    async_client: AsyncClient, db_session: AsyncSession, create_user, auth_header
) -> None:
    """Тест создания новой задачи."""

    _ = await create_user(USER_TRUE_EMAIL, USER_TRUE_USERNAME, USER_TRUE_PASSWORD)
    true_header = await auth_header(USER_TRUE_EMAIL, USER_TRUE_PASSWORD)

    payload = {
        "title": TITLE,
        "description": DESCRIPTION,
        "is_completed": IS_COMPLETED,
    }

    response = await async_client.post("/tasks", json=payload, headers=true_header)
    data = response.json()
    task_in_db = await db_session.get(Task, data["id"])

    assert response.status_code == 201
    assert "id" in data
    assert task_in_db is not None
    assert task_in_db.title == data["title"]
    assert task_in_db.description == data["description"]
    assert task_in_db.completed is False


@pytest.mark.asyncio
async def test_get_task(async_client: AsyncClient, create_user, auth_header) -> None:
    """Тест получения задачи по ID."""
    true_user = await create_user(
        USER_TRUE_EMAIL, USER_TRUE_USERNAME, USER_TRUE_PASSWORD
    )
    true_header = await auth_header(USER_TRUE_EMAIL, USER_TRUE_PASSWORD)

    payload = {"title": TITLE, "description": DESCRIPTION}
    response = await async_client.post("/tasks", json=payload, headers=true_header)
    assert response.status_code == 201
    task = response.json()

    response = await async_client.get(f"/tasks/{task['id']}", headers=true_header)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "test title"
    assert data["description"] == "test description"
    assert data["user_id"] == true_user.id


@pytest.mark.asyncio
async def test_get_all_tasks(
    async_client: AsyncClient, create_user, auth_header
) -> None:
    """Тест получения всех задач."""
    _ = await create_user(USER_TRUE_EMAIL, USER_TRUE_USERNAME, USER_TRUE_PASSWORD)
    true_header = await auth_header(USER_TRUE_EMAIL, USER_TRUE_PASSWORD)

    for i in range(2):
        payload = {"title": f"{TITLE} {i}", "description": f"{DESCRIPTION} {i}"}
        response = await async_client.post("/tasks", json=payload, headers=true_header)
        assert response.status_code == 201

    response = await async_client.get("/tasks", headers=true_header)
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert any(task["title"] == "test title 0" for task in tasks)
    assert any(task["title"] == "test title 1" for task in tasks)


@pytest.mark.asyncio
async def test_update_task(async_client: AsyncClient, create_user, auth_header) -> None:
    """Тест обновления задачи."""
    _ = await create_user(USER_TRUE_EMAIL, USER_TRUE_USERNAME, USER_TRUE_PASSWORD)
    true_header = await auth_header(USER_TRUE_EMAIL, USER_TRUE_PASSWORD)

    _ = await create_user(USER_FALSE_EMAIL, USER_FALSE_USERNAME, USER_FALSE_PASSWORD)
    false_header = await auth_header(USER_FALSE_EMAIL, USER_FALSE_PASSWORD)

    payload = {"title": TITLE, "description": DESCRIPTION}
    response = await async_client.post("/tasks", json=payload, headers=true_header)
    assert response.status_code == 201
    task = response.json()
    check = await async_client.get(f"/tasks/{task['id']}", headers=true_header)
    assert check.status_code == 200

    new_payload = {"title": NEW_TITLE, "description": NEW_DESCRIPTION}
    response = await async_client.put(
        f"/tasks/{task['id']}", json=new_payload, headers=true_header
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == NEW_TITLE
    assert updated["description"] == NEW_DESCRIPTION

    response_with_false_header = await async_client.put(
        f"/tasks/{task['id']}", json=new_payload, headers=false_header
    )
    assert response_with_false_header.status_code == 403


@pytest.mark.asyncio
async def test_delete_task(async_client: AsyncClient, create_user, auth_header) -> None:
    """Тест удаления задачи."""
    _ = await create_user(USER_TRUE_EMAIL, USER_TRUE_USERNAME, USER_TRUE_PASSWORD)
    true_header = await auth_header(USER_TRUE_EMAIL, USER_TRUE_PASSWORD)

    _ = await create_user(USER_FALSE_EMAIL, USER_FALSE_USERNAME, USER_FALSE_PASSWORD)
    false_header = await auth_header(USER_FALSE_EMAIL, USER_FALSE_PASSWORD)

    payload = {"title": TITLE, "description": DESCRIPTION}
    response = await async_client.post("/tasks", json=payload, headers=true_header)
    assert response.status_code == 201
    task = response.json()

    response_with_false_header = await async_client.delete(
        f"/tasks/{task['id']}", headers=false_header
    )
    assert response_with_false_header.status_code == 403

    response = await async_client.delete(f"/tasks/{task['id']}", headers=true_header)
    assert response.status_code in (200, 204)

    response = await async_client.get(f"/tasks/{task['id']}", headers=true_header)
    assert response.status_code == 404
