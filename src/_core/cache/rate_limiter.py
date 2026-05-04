class RateLimiter:
    def __init__(self, prefix: str = "ratelimit:"):
        self.prefix = prefix

    async def is_allowed(self, key: str, limit: int = 100, window: int = 60) -> bool:
        from .redis_client import redis_manager
        redis_key = f"{self.prefix}{key}"
        current = await redis_manager.async_client.incr(redis_key)
        if current == 1:
            await redis_manager.async_client.expire(redis_key, window)
        return current <= limit

    async def get_remaining(self, key: str, limit: int) -> int:
        from .redis_client import redis_manager
        redis_key = f"{self.prefix}{key}"
        current = await redis_manager.async_client.get(redis_key)
        current = int(current) if current else 0
        return max(0, limit - current)
