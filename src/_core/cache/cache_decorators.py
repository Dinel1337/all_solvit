import json
import hashlib
from functools import wraps
from typing import Any, Callable

def cache(ttl: int = 300, key_prefix: str = ""):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from .redis_client import redis_manager
            cache_key = f"{key_prefix or func.__name__}:{_make_cache_key(args, kwargs)}"
            cached = await redis_manager.async_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            await redis_manager.async_client.setex(cache_key, ttl, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator

def _make_cache_key(args, kwargs) -> str:
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()
