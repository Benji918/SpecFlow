import json
from typing import Any, Optional, Union
import redis.asyncio as redis
from app.config import settings

class CacheService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None

    async def set(self, key: str, value: Any, expire: int = 600):
        """Set a value in cache with expiration (default 5 mins)."""
        try:
            await self.redis.set(key, json.dumps(value), ex=expire)
        except Exception as e:
            print(f"Cache set error: {e}")

    async def delete(self, key: str):
        """Delete a key from cache."""
        try:
            await self.redis.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")

    async def delete_pattern(self, pattern: str):
        """Delete keys matching a pattern."""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
        except Exception as e:
            print(f"Cache delete_pattern error: {e}")

cache_service = CacheService()
