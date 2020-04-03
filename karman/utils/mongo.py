from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from fastapi_helpers import app_dependency
from karman.app import app
from karman.config import app_config


@app_dependency(app)
async def get_db() -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(app_config.mongodb)
    yield client.get_default_database("default")
    client.close()
