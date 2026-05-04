import json
from typing import Optional, Dict, Any

class RedisSessionStorage:
    def __init__(self, prefix: str = "session:"):
        self.prefix = prefix

    async def create_session(self, user_id: str, data: Dict[str, Any], ttl: int = 3600) -> str:
        from .redis_client import redis_manager
        session_key = f"{self.prefix}{user_id}"
        await redis_manager.async_client.setex(session_key, ttl, json.dumps(data))
        return session_key

    async def get_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        from .redis_client import redis_manager
        session_key = f"{self.prefix}{user_id}"
        data = await redis_manager.async_client.get(session_key)
        return json.loads(data) if data else None

    async def delete_session(self, user_id: str):
        from .redis_client import redis_manager
        session_key = f"{self.prefix}{user_id}"
        await redis_manager.async_client.delete(session_key)
