from bson import CodecOptions
from bson.codec_options import TypeRegistry
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from fastapi_helpers import app_dependency
from karman.app import app
from karman.config import app_config
from motor_odm.encoders import SetEncoder, FrozensetEncoder


@app_dependency(app)
async def get_db() -> AsyncIOMotorDatabase:
    encoders = [SetEncoder(), FrozensetEncoder()]
    codec_options = CodecOptions(type_registry=TypeRegistry(encoders))
    client = AsyncIOMotorClient(app_config.mongodb, codec_options=codec_options)
    db = client.get_default_database("local")
    yield db
    client.close()
