import aioredis

from fastapi_helpers import app_dependency
from karman.app import app
from karman.config import app_config


@app_dependency(app)
async def get_redis() -> aioredis.Redis:
    print("Redis Init")
    pool = await aioredis.create_redis_pool(app_config.redis)
    yield pool
    pool.close()
    await pool.wait_closed()
    print("Redis Closed")
