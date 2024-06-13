from typing import Annotated
from urllib.parse import unquote_plus

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from arona_helper_backend.config import config
from arona_helper_backend.models import LoginData
from arona_helper_backend.utils import (
    FavourQueryAPI,
    get_login_data,
)

nick_router = APIRouter(prefix="/nick")
API = FavourQueryAPI(base_url=config.upstream.url)


@nick_router.get(
    path="",
    name="获取用户昵称",
    description="获取用户昵称。",
    responses={
        200: {
            "description": "获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "data": {
                            "uid": 123456,
                            "nick": "nick",
                        },
                    },
                },
            },
        },
    },
)
async def get_nick(uid: str) -> JSONResponse:
    nick = await API.nick_edit(uid=uid)
    return JSONResponse(
        content={
            "status": 200,
            "data": {
                "uid": uid,
                "nick": unquote_plus(nick.msg),
            },
        },
    )


@nick_router.put(
    path="",
    name="修改用户昵称",
    description="修改用户昵称。",
    responses={
        200: {
            "description": "修改成功",
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "data": {
                            "result": "success",
                            "current": {
                                "uid": 123456,
                                "nick": "new_nick",
                            },
                        },
                    },
                },
            },
        },
        403: {
            "description": "修改失败",
            "content": {
                "application/json": {
                    "example": {
                        "status": 403,
                        "msg": "error message",
                    },
                },
            },
        },
    },
)
async def put_nick(
    nick: str,
    user_profile: Annotated[LoginData, Depends(get_login_data)],
) -> JSONResponse:
    uid = user_profile.user_id
    result = await API.nick_edit(uid, nick)
    return JSONResponse(
        content={
            "status": 200,
            "data": {
                "result": result.msg,
                "current": {
                    "uid": uid,
                    "nick": nick,
                },
            },
        },
    )
