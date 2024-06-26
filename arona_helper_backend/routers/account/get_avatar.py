import httpx
from fastapi import APIRouter
from fastapi.responses import Response

from arona_helper_backend.config import config
from arona_helper_backend.databases.cache.redis import get_redis_connection
from arona_helper_backend.exceptions import AronaError
from arona_helper_backend.utils import FavourQueryAPI

avatar_router = APIRouter(prefix="/avatar")

AVATAR_EXPIRE_TIME = 60 * 60 * 6

FAVOR_API = FavourQueryAPI(config.upstream.url, config.upstream.token)


@avatar_router.get(
    "",
    name="获取头像",
    description="返回头像 bytes",
    responses={
        200: {
            "description": "获取成功",
            "content": {"image/png": {"example": b"buffer"}},
        },
    },
)
async def get_avatar(uid: str) -> Response:
    redis_conn = await get_redis_connection()
    if await redis_conn.exists(f"cache:avatar:{uid}"):
        avatar: bytes | None = await redis_conn.get(f"cache:avatar:{uid}")
        if avatar is not None:
            print(f"> [{uid}] Successfully get avatar from cache.")
            return Response(content=avatar, media_type="image/png", status_code=200)
    print(f"> [{uid}] Avatar not found in cache, fetching from qlogo.")
    try:
        real_id = (await FAVOR_API.get_real_id(uid)).id
    except httpx.HTTPError as e:
        raise AronaError("[!!!] Mapping Error [!!!]", 408) from e
    print(f"> [{uid}] Mapping: {uid} <-> {real_id}")
    try:
        async with httpx.AsyncClient() as client:
            response = (
                await client.get(
                    f"https://q.qlogo.cn/qqapp/{config.secret.bot_appid}/{real_id}/640",
                )
            ).raise_for_status()
    except httpx.HTTPError as e:
        raise AronaError("获取头像失败", 408) from e
    await redis_conn.set(
        f"cache:avatar:{uid}",
        response.content,
        nx=True,
        ex=AVATAR_EXPIRE_TIME,
    )
    print(f"> [{uid} -> {real_id}] Successfully get avatar from qlogo.")
    return Response(content=response.content, media_type="image/png", status_code=200)
