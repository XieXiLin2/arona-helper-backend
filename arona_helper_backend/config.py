import yaml
from pydantic import BaseModel
from pydantic.networks import AnyHttpUrl
from pydantic.fields import Field
from typing import Annotated
from pathlib import Path
from cookit.pyd import type_validate_python


CONFIG_FILE = Path().cwd() / "config.yml"


class DatabaseConfigModel(BaseModel):
    dialect: str
    driver: str | None = None
    host: str
    port: int | None = None
    username: str
    password: str
    db: str
    args: str | None = None
    debug: bool


class FastAPIConfigModel(BaseModel):
    host: str = "0.0.0.0"
    port: int = Field(default=8080, ge=1, le=65535)
    debug: bool = False
    reload: bool = False
    log_level: int | str = "info"
    title: str = "Arona Helper Backend"
    description: str = "Arona Helper Backend API"


class ConfigModel(BaseModel):
    jwt_token: str
    upstream: Annotated[str, AnyHttpUrl]
    bawiki_data: Annotated[str, AnyHttpUrl]
    fastapi: FastAPIConfigModel
    database: DatabaseConfigModel


config: ConfigModel = type_validate_python(
    ConfigModel, yaml.safe_load(CONFIG_FILE.read_text())
)
