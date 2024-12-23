# 用于连接 Redis 数据库的模块

from redis.asyncio import Redis, ConnectionPool
from typing import Optional
from .config import redis_connections, redis_url


class RedisClient:

    def __init__(self, redis_url: str = redis_url):
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        # 设置连接池的最大连接数
        # 使用 redis.asyncio 创建带有连接池的 Redis 客户端
        pool = ConnectionPool.from_url(
            self.redis_url, max_connections=redis_connections, decode_responses=True
        )
        self.redis = Redis(connection_pool=pool)

    """
    存储和获取accesstoken，key
    """

    # 设置全局的 access_token
    async def set_access_token(self, access_token: str):
        await self.redis.set("access_token", access_token, ex=5000)

    # 获取全局的 access_token
    async def get_access_token(self) -> Optional[str]:
        return await self.redis.get("access_token")

    # 关闭 Redis 连接
    async def close(self):
        if self.redis:
            await self.redis.close()
            await self.redis.connection_pool.disconnect()  # 确保连接池也关闭


# 创建全局的 redis 实例
redis_client = RedisClient()
