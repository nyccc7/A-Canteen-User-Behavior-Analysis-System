import os
import motor.motor_asyncio
import redis.asyncio as redis
from typing import Optional

# MongoDB Configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "cafeteria_db"

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://:inspire123@localhost:6379")

class Database:
    client: motor.motor_asyncio.AsyncIOMotorClient = None
    db = None
    redis_client: redis.Redis = None

    async def connect_db(self):
        """Connect to MongoDB and Redis."""
        # MongoDB
        self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        print(f"Connected to MongoDB at {MONGO_URL}")

        # Redis
        self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        try:
            await self.redis_client.ping()
            print(f"Connected to Redis at {REDIS_URL}")
        except redis.ConnectionError:
            print("Failed to connect to Redis")

    async def close_db(self):
        """Close database connections."""
        if self.client:
            self.client.close()
        if self.redis_client:
            await self.redis_client.close()

db = Database()

async def get_database():
    return db.db

async def get_redis():
    return db.redis_client
