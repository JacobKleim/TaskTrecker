from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.manager import BaseUserManager
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.core.config import load_config
from app.api.db.database import get_async_session
from app.api.db.models import User


config = load_config()


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


class UserManager(BaseUserManager[User, int]):
    def parse_id(self, user_id: str) -> int:
        return int(user_id)


async def get_jwt_strategy() -> AsyncGenerator[JWTStrategy, None]:
    yield JWTStrategy(
        secret=config.jwt.secret_key,
        lifetime_seconds=config.jwt.access_token_expire_seconds,
    )


async def get_user_db(
    db: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield SQLAlchemyUserDatabase(db, User)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_backend],
)
