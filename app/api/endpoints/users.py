from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_users.manager import BaseUserManager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.core.auth_settings import fastapi_users, get_user_manager
from app.api.db.database import get_async_session
from app.api.db.models import User
from app.api.schemas.user import UserCreate, UserRead, UserUpdate


router = APIRouter()
get_current_user = fastapi_users.current_user()


@router.post("/users", status_code=201, response_model=UserRead)
async def register(
    user: UserCreate,
    user_manager: BaseUserManager[User, int] = Depends(get_user_manager),
) -> UserRead:
    """Создание пользователя."""
    created_user = await user_manager.create(user)
    return created_user


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> UserRead:
    """Получение информации о пользователе."""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users", response_model=List[UserRead])
async def get_all_users(
    session: AsyncSession = Depends(get_async_session),
) -> List[UserRead]:
    """Получение всех пользователей."""
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users


@router.put("/users/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserRead = Depends(get_current_user),
) -> UserRead:
    """Обновление информации о пользователе."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden: cannot update other users")
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.email = user_update.email
    user.username = user_update.username
    await session.commit()
    await session.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserRead = Depends(get_current_user),
) -> None:
    """Удаление пользователя."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden: cannot delete other users")
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await session.delete(user)
    await session.commit()
