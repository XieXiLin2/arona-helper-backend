from contextlib import asynccontextmanager
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from arona_helper_backend.config import config
from arona_helper_backend.databases.cache.redis import (
    close_connection_pool,
    start_connection_pool,
)
from arona_helper_backend.databases.data.sql.database import close_engine, init_engine
from arona_helper_backend.exceptions import AronaError, arona_error_handler
from arona_helper_backend.routers import base_router
from arona_helper_backend.utils import db_keep_alive

__VERSION__ = "0.1.0"


STATIC_PATH = Path(__file__).parent / "static"
SCHEDULER = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(application: FastAPI):  # noqa: ARG001
    await start_connection_pool()
    await init_engine(
        user=config.database.mysql.user,
        password=config.database.mysql.password,
        host=config.database.mysql.host,
        port=config.database.mysql.port,
        dbname=config.database.mysql.database,
    )
    SCHEDULER.add_job(db_keep_alive, "interval", seconds=30)
    SCHEDULER.start()
    yield
    await close_connection_pool()
    await close_engine()
    SCHEDULER.shutdown()


app = FastAPI(
    title=config.fastapi.title,
    description=config.fastapi.description,
    version=__VERSION__,
    contact={
        "name": "FalfaChino",
    },
    license_info={
        "name": "MIT",
        "url": r"https://zh.wikipedia.org/wiki/MIT%E8%A8%B1%E5%8F%AF%E8%AD%89",
    },
    lifespan=lifespan,
    swagger_ui_parameters={},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=base_router)

app.exception_handler(AronaError)(arona_error_handler)


@app.get(
    path="/",
    description="获取 API 信息",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "data": {
                            "name": config.fastapi.title,
                            "description": config.fastapi.description,
                            "version": __VERSION__,
                        },
                    },
                },
            },
        },
    },
)
async def root() -> JSONResponse:
    return JSONResponse(
        content={
            "status": 200,
            "data": {
                "name": config.fastapi.title,
                "description": config.fastapi.description,
                "version": __VERSION__,
            },
        },
        status_code=200,
    )


app.mount("/", StaticFiles(directory=STATIC_PATH, follow_symlink=True), "StaticFiles")
