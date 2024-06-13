import httpx
from fastapi import APIRouter
from fastapi.responses import Response

from arona_helper_backend.config import config
from arona_helper_backend.utils import FavourQueryAPI

avatar_router = APIRouter(prefix="/avatar")

FAVOR_API = FavourQueryAPI(config.upstream.url, config.upstream.token)


@avatar_router.get(
    "",
    name="获取头像",
    description="返回头像 bytes",
    responses={
        200: {
            "description": "获取成功",
            "content": {"image/png": {}},
        },
    },
)
async def get_avatar(uid: str) -> Response:
    real_id = (await FAVOR_API.get_real_id(uid)).id
    async with httpx.AsyncClient() as client:
        response = (
            await client.get(
                f"https://q.qlogo.cn/qqapp/{config.secret.bot_appid}/{real_id}/640",
            )
        ).raise_for_status()
    return Response(content=response.content, media_type="image/png", status_code=200)
