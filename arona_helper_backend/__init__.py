from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from arona_helper_backend.config import config
from arona_helper_backend.routers import base_router
from arona_helper_backend.databases.cache.redis import (
    start_connection_pool,
    close_connection_pool,
)
from arona_helper_backend.databases.data.sql.database import init_engine, close_engine

__VERSION__ = "0.1.0"


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
    yield
    await close_connection_pool()
    await close_engine()


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
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=base_router)


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
