from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from arona_helper_backend.config import config
from arona_helper_backend.routers import base_router

__VERSION__ = "0.1.0"

app = FastAPI(
    debug=config.fastapi.debug,
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
        }
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
