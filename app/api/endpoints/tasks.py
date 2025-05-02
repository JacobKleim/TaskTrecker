from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.core.auth_settings import fastapi_users
from app.api.db.database import get_async_session
from app.api.db.models import Task
from app.api.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.api.schemas.user import UserRead


get_current_user = fastapi_users.current_user()


router = APIRouter()


@router.post("/tasks", status_code=201, response_model=TaskRead)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: UserRead = Depends(get_current_user),
) -> TaskRead:
    """Создание задачи."""
    db_task = Task(title=task.title, description=task.description, user_id=current_user.id)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


@router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserRead = Depends(get_current_user),
) -> TaskRead:
    """Получение информации о задаче."""
    result = await session.execute(select(Task).where(Task.id == task_id, Task.user_id == current_user.id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/tasks", response_model=List[TaskRead])
async def get_all_tasks(
    session: AsyncSession = Depends(get_async_session),
) -> List[TaskRead]:
    """Получение всех задач у пользователя."""
    result = await session.execute(select(Task))
    tasks = result.scalars().all()
    return tasks


@router.put("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserRead = Depends(get_current_user),
) -> TaskRead:
    """Обновление информации о задаче."""
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    task.title = task_update.title
    task.description = task_update.description
    task.completed = task_update.completed
    await session.commit()
    await session.refresh(task)
    return task


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserRead = Depends(get_current_user),
) -> None:
    """Удаление задачи."""
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    await session.delete(task)
    await session.commit()
    return task
