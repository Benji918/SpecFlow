import json
from typing import Any, Optional, Union
import redis.asyncio as redis
from app.config import settings

class CacheService:
    def __init__(self):
        # Upstash Redis requires TLS connection - use rediss:// protocol
        # Also add connection pooling and better error handling
        self.redis = redis.from_url(
            settings.REDIS_URL.replace('redis://', 'rediss://') if 'rediss://' in settings.REDIS_URL else settings.REDIS_URL,  # Force TLS
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
        except redis.ConnectionError as e:
            print(f"Cache connection error: {e}")
            # Try to reconnect
            await self._reconnect()
        except Exception as e:
            print(f"Cache get error: {e}")
        return None

    async def _reconnect(self):
        """Attempt to reconnect to Redis."""
        try:
            await self.redis.ping()
        except:
            # Create new connection
            self.redis = redis.from_url(
               settings.REDIS_URL.replace('redis://', 'rediss://') if 'rediss://' in settings.REDIS_URL else settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )

    async def set(self, key: str, value: Any, expire: int = 600):
        """Set a value in cache with expiration (default 10 mins)."""
        try:
            await self.redis.set(key, json.dumps(value), ex=expire)
        except redis.ConnectionError as e:
            print(f"Cache connection error: {e}")
            await self._reconnect()
        except Exception as e:
            print(f"Cache set error: {e}")

    async def delete(self, key: str):
        """Delete a key from cache."""
        try:
            await self.redis.delete(key)
        except redis.ConnectionError as e:
            print(f"Cache connection error: {e}")
            await self._reconnect()
        except Exception as e:
            print(f"Cache delete error: {e}")

    async def delete_pattern(self, pattern: str):
        """Delete keys matching a pattern."""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
        except redis.ConnectionError as e:
            print(f"Cache connection error: {e}")
            await self._reconnect()
        except Exception as e:
            print(f"Cache delete_pattern error: {e}")

cache_service = CacheService()
