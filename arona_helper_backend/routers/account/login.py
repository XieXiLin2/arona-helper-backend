from time import time
from typing import Annotated

import jwt
from cookit.pyd import model_dump
from cookit.pyd.compat import type_validate_python
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials

from arona_helper_backend.config import config
from arona_helper_backend.databases.cache.redis import get_redis_connection
from arona_helper_backend.models import LoginData
from arona_helper_backend.utils import (
    bot_verify_bearer,
    rs_generator,
    user_verify_bearer,
)

login_router = APIRouter(prefix="/login")

CODE_EXPIRE_TIME = 120

LOGIN_EXPIRE_TIME = 60 * 60 * 24 * 7


@login_router.get(
    path="/code/get",
    name="获取登录验证码",
    description=f"获取登录验证码，返回验证码，有效期 {CODE_EXPIRE_TIME} 秒。",
    responses={
        200: {
            "description": "获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "data": {
                            "auth_code": "BASRT9",
                            "exp": CODE_EXPIRE_TIME,
                        },
                    },
                },
            },
        },
    },
)
async def get_auth_code() -> JSONResponse:
    redis_conn = await get_redis_connection()
    auth_code = rs_generator(size=6)
    await redis_conn.set(
        name=f"login:auth_code:{auth_code}",
        value="",
        ex=CODE_EXPIRE_TIME,
    )
    return JSONResponse(
        content={
            "status": 200,
            "data": {
                "auth_code": auth_code,
                "exp": CODE_EXPIRE_TIME,
            },
        },
        status_code=200,
    )


@login_router.post(
    path="/code/bot/call",
    name="机器人调用验证",
    description="机器人调用验证接口，传递用户 ID 和 code，需要带上机器人专用的 Bearer Token。",
    responses={
        200: {
            "description": "传递成功",
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "msg": "传递成功",
                    },
                },
            },
        },
        401: {
            "description": "未授权",
            "content": {
                "application/json": {
                    "example": {
                        "status": 401,
                        "msg": "未授权",
                    },
                },
            },
        },
        403: {
            "description": "已被使用",
            "content": {
                "application/json": {
                    "example": {
                        "status": 403,
                        "msg": "已被使用",
                    },
                },
            },
        },
        404: {
            "description": "未找到 code",
            "content": {
                "application/json": {
                    "example": {
                        "status": 404,
                        "msg": "未找到 code",
                    },
                },
            },
        },
    },
)
async def bot_call_verify(
    code: str,
    user_id: str,
    bot_token: Annotated[HTTPAuthorizationCredentials, Depends(bot_verify_bearer)],
) -> JSONResponse:
    if bot_token.credentials != config.secret.bot_req_token:
        return JSONResponse({"status": 401, "msg": "未授权"}, status_code=401)
    redis_conn = await get_redis_connection()
    auth: bytes | None = await redis_conn.get(f"login:auth_code:{code}")
    if auth is not None and auth.decode("UTF-8") != "":
        return JSONResponse({"status": 403, "msg": "已被使用"}, status_code=403)
    if await redis_conn.set(name=f"login:auth_code:{code}", value=user_id, xx=True):
        return JSONResponse({"status": 200, "msg": "传递成功"}, status_code=200)
    return JSONResponse({"status": 404, "msg": "未找到 code"}, status_code=403)


@login_router.get(
    path="/code/check",
    name="检查验证状态",
    description="获取用户是否完成验证，完成则返回 token。",
    responses={
        200: {
            "description": "验证成功",
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "data": {
                            "token": "JWT_Token",
                            "expire_on": 114514,
                        },
                    },
                },
            },
        },
        403: {
            "description": "未完成验证",
            "content": {
                "application/json": {
                    "example": {
                        "status": 401,
                        "msg": "未完成验证",
                    },
                },
            },
        },
        404: {
            "description": "未找到 code",
            "content": {
                "application/json": {
                    "example": {
                        "status": 404,
                        "msg": "未找到 code",
                    },
                },
            },
        },
    },
)
async def check_auth_code(code: str) -> JSONResponse:
    redis_conn = await get_redis_connection()
    if await redis_conn.exists(f"login:auth_code:{code}"):
        auth: bytes | None = await redis_conn.get(f"login:auth_code:{code}")
        if auth is not None and auth.decode("UTF-8") != "":
            user_id: str = await redis_conn.get(f"login:auth_code:{code}")
            await redis_conn.delete(f"login:auth_code:{code}")
            login_form = LoginData(
                user_id=user_id,
                exp=int(time()) + LOGIN_EXPIRE_TIME,
            )
            lg_token = jwt.encode(
                payload=model_dump(login_form),
                key=config.secret.jwt_secret,
                algorithm=config.secret.jwt_algorithm,
            )
            return JSONResponse(
                {
                    "status": 200,
                    "data": {"token": lg_token, "expire_on": login_form.exp},
                },
                status_code=200,
            )
        return JSONResponse({"status": 403, "msg": "未完成验证"}, status_code=401)
    return JSONResponse({"status": 404, "msg": "未找到 code"}, status_code=403)


@login_router.post(
    path="/code/refresh",
    name="刷新 token",
    description="刷新 token，需要提供原 token。",
    responses={
        200: {
            "description": "刷新成功",
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "data": {
                            "token": "JWT_Token",
                            "expire_on": 114514,
                        },
                    },
                },
            },
        },
        401: {
            "description": "token 过期",
            "content": {
                "application/json": {
                    "example": {
                        "status": 401,
                        "msg": "token 过期，请重新登录",
                    },
                },
            },
        },
        404: {
            "description": "无效 token",
            "content": {
                "application/json": {
                    "example": {
                        "status": 404,
                        "msg": "无效 token",
                    },
                },
            },
        },
    },
)
async def refresh_token(
    auth: Annotated[HTTPAuthorizationCredentials, Depends(user_verify_bearer)],
) -> JSONResponse:
    token = auth.credentials
    try:
        login_data = jwt.decode(
            jwt=token,
            key=config.secret.jwt_secret,
            algorithms=[config.secret.jwt_algorithm],
        )
        login_form = type_validate_python(LoginData, login_data)
        login_form.exp = int(time()) + LOGIN_EXPIRE_TIME
        lg_token = jwt.encode(
            payload=model_dump(login_form),
            key=config.secret.jwt_secret,
            algorithm=config.secret.jwt_algorithm,
        )
        return JSONResponse(
            {"status": 200, "data": {"token": lg_token, "expire_on": login_form.exp}},
            status_code=200,
        )
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            {"status": 401, "msg": "token 过期，请重新登录"},
            status_code=401,
        )
    except jwt.InvalidTokenError:
        return JSONResponse({"status": 404, "msg": "无效 token"}, status_code=403)
