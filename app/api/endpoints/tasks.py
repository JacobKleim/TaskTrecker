"""
Маршруты API для задач (tasks).

Вызывают методы из слоя сервисов.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_settings import fastapi_users
from app.db.database import get_async_session
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.schemas.user import UserRead
from app.services.task_service import TaskService

logger = logging.getLogger(__name__)

get_current_user = fastapi_users.current_user()
router = APIRouter()


@router.post("/tasks", status_code=201, response_model=TaskRead)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserRead = Depends(get_current_user),
) -> TaskRead:
    return await TaskService.create_task(task, db, current_user)


@router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserRead = Depends(get_current_user),
) -> TaskRead:
    return await TaskService.get_task(task_id, db, current_user)


@router.get("/tasks", response_model=List[TaskRead])
async def get_all_tasks(
    db: AsyncSession = Depends(get_async_session),
) -> List[TaskRead]:
    return await TaskService.get_all_tasks(db)


@router.put("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserRead = Depends(get_current_user),
) -> TaskRead:
    return await TaskService.update_task(task_id, task_update, db, current_user)


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserRead = Depends(get_current_user),
) -> None:
    return await TaskService.delete_task(task_id, db, current_user)
