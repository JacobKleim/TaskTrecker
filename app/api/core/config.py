from dataclasses import dataclass

from environs import Env


@dataclass
class JWTConfig:
    secret_key: str
    access_token_expire_seconds: int


@dataclass
class DatabaseConfig:
    database_url: str


@dataclass
class Config:
    db: DatabaseConfig
    jwt: JWTConfig
    debug: bool


def load_config(path: str = "./.env") -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        db=DatabaseConfig(database_url=env("DATABASE_URL")),
        jwt=JWTConfig(
            secret_key=env("SECRET_KEY"),
            access_token_expire_seconds=env.int("ACCESS_TOKEN_EXPIRE_SECONDS", default=5000),
        ),
        debug=env.bool("DEBUG", default=False),
    )
