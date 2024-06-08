from pathlib import Path
from typing import Annotated

import yaml
from cookit.pyd import type_validate_python
from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.networks import AnyHttpUrl

CONFIG_FILE = Path().cwd() / "config.yml"


class RedisConfigModel(BaseModel):
    url: str


class MySQLConfigModel(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str
    chatset: str = "utf8mb4"


class DatabaseConfigModel(BaseModel):
    redis: RedisConfigModel
    mysql: MySQLConfigModel


class FastAPIConfigModel(BaseModel):
    host: str = "0.0.0.0"  # noqa: S104
    port: int = Field(default=8080, ge=1, le=65535)
    log_level: int | str = "info"
    title: str = "Arona Helper Backend"
    description: str = "Arona Helper Backend API"


class SecretConfigModel(BaseModel):
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    bot_req_token: str


class ConfigModel(BaseModel):
    secret: SecretConfigModel
    upstream: Annotated[str, AnyHttpUrl]
    bawiki_data: Annotated[str, AnyHttpUrl]
    fastapi: FastAPIConfigModel
    database: DatabaseConfigModel


config: ConfigModel = type_validate_python(
    ConfigModel,
    yaml.safe_load(CONFIG_FILE.read_text()),
)
