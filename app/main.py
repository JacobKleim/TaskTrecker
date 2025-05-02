from fastapi import FastAPI

from app.api.core.auth_settings import auth_backend, fastapi_users
from app.api.endpoints import tasks, users


app = FastAPI()


app.include_router(users.router, tags=["users"])
app.include_router(tasks.router, tags=["tasks"])
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
