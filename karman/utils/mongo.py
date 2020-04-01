from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from fastapi_helpers import app_dependency
from karman.app import app
from karman.config import app_config


@app_dependency(app)
async def get_mongo() -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(app_config.mongodb)
    yield client
    client.close()


async def get_db(mongo: AsyncIOMotorClient = Depends(get_mongo)) -> AsyncIOMotorDatabase:
    return mongo.get_default_database("default")
