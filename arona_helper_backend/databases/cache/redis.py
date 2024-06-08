import redis.asyncio as redis

from arona_helper_backend.config import config

# 更正变量名拼写错误
REDIS_CONNECTION_POOL = None  # type: ignore[reportAssignmentType]


async def start_connection_pool() -> None:
    global REDIS_CONNECTION_POOL
    if not REDIS_CONNECTION_POOL:
        try:
            REDIS_CONNECTION_POOL = redis.ConnectionPool.from_url(
                url=config.database.redis.url,
            )
        except redis.RedisError as e:
            # 添加异常处理
            print(f"创建 Redis 连接池失败: {e}")
            raise


async def get_connection_pool() -> redis.ConnectionPool:
    global REDIS_CONNECTION_POOL
    if not REDIS_CONNECTION_POOL:
        await start_connection_pool()
        if not REDIS_CONNECTION_POOL:
            raise Exception("Redis 连接池未初始化")
    return REDIS_CONNECTION_POOL


async def get_redis_connection() -> redis.Redis:
    return redis.Redis(
        connection_pool=await get_connection_pool(),
    )  # 使用 connection_pool 参数


async def close_connection_pool() -> None:
    global REDIS_CONNECTION_POOL
    if REDIS_CONNECTION_POOL:
        try:
            await REDIS_CONNECTION_POOL.disconnect()
            REDIS_CONNECTION_POOL = None  # 断开连接后将全局变量重置为 None
        except redis.RedisError as e:
            # 添加异常处理
            print(f"关闭 Redis 连接池失败: {e}")
            raise
