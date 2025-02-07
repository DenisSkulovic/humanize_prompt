import aioredis
import json
from core.config import Config

class CacheService:
    """
    A utility class to handle Redis interactions asynchronously.
    """
    def __init__(self):
        self.host = Config.REDIS_HOST
        self.port = Config.REDIS_PORT
        self.db = Config.REDIS_DB
        self.ttl = Config.REDIS_TTL  # Default TTL of 1 hour
        self.client = None

    async def connect(self):
        """
        Establishes an asynchronous connection to Redis.
        """
        self.client = await aioredis.from_url(f"redis://{self.host}:{self.port}/{self.db}", decode_responses=True)
    
    async def set(self, key: str, value: dict, ttl: int = None):
        """
        Stores a key-value pair in Redis with an optional TTL.
        """
        if self.client is None:
            await self.connect()
        try:
            ttl = ttl if ttl is not None else self.ttl
            await self.client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            print(f"Redis set error: {e}")
    
    async def get(self, key: str):
        """
        Retrieves a value from Redis by key.
        """
        if self.client is None:
            await self.connect()
        try:
            value = await self.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    async def delete(self, key: str):
        """
        Deletes a key from Redis.
        """
        if self.client is None:
            await self.connect()
        try:
            await self.client.delete(key)
        except Exception as e:
            print(f"Redis delete error: {e}")
    
    async def exists(self, key: str) -> bool:
        """
        Checks if a key exists in Redis.
        """
        if self.client is None:
            await self.connect()
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
