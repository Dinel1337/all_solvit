import redis
from redis.asyncio import Redis as AsyncRedis
import os
from typing import Optional

class RedisManager:
    def __init__(self):
        self._client: Optional[AsyncRedis] = None
        self._sync_client: Optional[redis.Redis] = None

    async def init(self, redis_url: str = None):
        redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client = await AsyncRedis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20
        )
        self._sync_client = redis.Redis.from_url(redis_url, decode_responses=True)
        await self._client.ping()
        return self

    @property
    def async_client(self) -> AsyncRedis:
        if not self._client:
            raise RuntimeError("Redis not initialized")
        return self._client

    @property
    def sync_client(self) -> redis.Redis:
        if not self._sync_client:
            raise RuntimeError("Redis not initialized")
        return self._sync_client

    async def close(self):
        if self._client:
            await self._client.close()

redis_manager = RedisManager()
