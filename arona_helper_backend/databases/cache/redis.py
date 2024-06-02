import redis.asyncio as redis

from arona_helper_backend.config import config

REDIS_CONNTECTION_POOL: redis.ConnectionPool = None  # type: ignore[reportAssignmentType]


async def get_connection_pool() -> redis.ConnectionPool:
    global REDIS_CONNTECTION_POOL
    if not REDIS_CONNTECTION_POOL:
        REDIS_CONNTECTION_POOL = redis.ConnectionPool.from_url(
            url=config.database.redis.url,
        )
    return REDIS_CONNTECTION_POOL


async def get_redis_connection() -> redis.Redis:
    return redis.Redis.from_pool(await get_connection_pool())


async def close_connection_pool() -> None:
    global REDIS_CONNTECTION_POOL
    if REDIS_CONNTECTION_POOL:
        await REDIS_CONNTECTION_POOL.disconnect()
