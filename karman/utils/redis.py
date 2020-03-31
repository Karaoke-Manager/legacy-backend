import aioredis
from aioredis import Redis

from fastapi_helpers import app_dependency
from ..app import app
from ..config import app_config


@app_dependency(app)
async def redis() -> Redis:
    pool = await aioredis.create_redis_pool(app_config.redis)
    yield pool
    pool.close()
