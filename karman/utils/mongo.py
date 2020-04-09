from bson.codec_options import TypeRegistry
from fastapi_helpers import app_dependency
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from karman.app import app
from karman.config import app_config
from motor_odm import Document
from motor_odm.encoders import SetEncoder, FrozensetEncoder


@app_dependency(app)
async def get_db() -> AsyncIOMotorDatabase:
    encoders = [SetEncoder(), FrozensetEncoder()]
    client = AsyncIOMotorClient(app_config.mongodb, type_registry=TypeRegistry(encoders))
    db = client.get_default_database("local")
    Document.use(db)
    yield db
    client.close()
