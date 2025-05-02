from fastapi_users import schemas
from pydantic import ConfigDict, EmailStr


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(schemas.BaseUserUpdate):
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserRead(schemas.BaseUser):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)
