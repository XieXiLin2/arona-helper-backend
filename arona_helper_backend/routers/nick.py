from fastapi import APIRouter
from fastapi.responses import JSONResponse
from urllib.parse import unquote_plus

from arona_helper_backend.config import config
from arona_helper_backend.utils import FavourQueryAPI


nick_router = APIRouter(prefix="/nick")
API = FavourQueryAPI(base_url=config.upstream)


@nick_router.get(path="", description="获取用户昵称")
async def get_nick(uid: int) -> JSONResponse:
    nick = await API.nick_edit(uid)
    return JSONResponse(
        content={
            "status": 200,
            "data": {
                "uid": uid,
                "nick": unquote_plus(nick.msg),
            },
        },
    )


# @nick_router.put(path="", description="修改用户昵称")
# async def put_nick(uid: int, nick: str) -> JSONResponse:
#     result = await API.nick_edit(uid, nick)
#     return JSONResponse(
#         content={
#             "status": 200,
#             "data": {
#                 "result": result.msg,
#                 "current": {
#                     "uid": uid,
#                     "nick": nick,
#                 },
#             },
#         },
#     )
