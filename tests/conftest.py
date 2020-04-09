import pytest
from aioredis import Redis
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient

import karman
from data import Dataset
from karman.config import app_config
from karman.utils import get_db, aioredis, get_redis, TypeRegistry
from motor_odm import Document
from motor_odm.encoders import SetEncoder, FrozensetEncoder


@pytest.fixture(scope='function', autouse=True)
async def db(worker_id: str) -> AsyncIOMotorDatabase:
    encoders = [SetEncoder(), FrozensetEncoder()]
    mongo = AsyncIOMotorClient(app_config.test.mongo or app_config.mongodb, type_registry=TypeRegistry(encoders))
    db_name = f"{app_config.test.db_prefix}{worker_id}"
    await mongo.drop_database(db_name)
    yield mongo[db_name]
    await mongo.drop_database(db_name)
    mongo.close()


@pytest.fixture(scope='function', autouse=True)
async def redis(worker_id: str) -> Redis:
    if worker_id == "master":
        index = 1
    else:
        index = int(worker_id[2:]) + app_config.test.redis_offset
    pool = await aioredis.create_redis_pool(app_config.test.redis or app_config.redis, db=index)
    yield pool
    await pool.flushdb()
    pool.close()
    await pool.wait_closed()


@pytest.fixture(scope='function')
async def app(db: AsyncIOMotorDatabase, redis: Redis) -> FastAPI:
    async def get_test_db():
        yield db

    async def get_test_redis():
        yield redis

    karman.app.dependency_overrides[get_db] = get_test_db
    karman.app.dependency_overrides[get_redis] = get_test_redis
    async with LifespanManager(karman.app):
        Document.use(db)
        yield karman.app


@pytest.fixture(scope='function')
async def client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://app.io") as client:
        yield client


@pytest.fixture(scope='function')
async def dataset(db: AsyncIOMotorDatabase) -> Dataset:
    dataset = Dataset()
    Document.use(db)
    await dataset.load()
    return dataset


@pytest.fixture(name="login:admin", scope="function")
async def login_admin(client: AsyncClient, dataset: Dataset):
    response = await client.post("/v1/login", data={
        "username": dataset.admin.username,
        "password": dataset.ADMIN_PASSWORD
    })
    client.headers["Authorization"] = f"Bearer {response.json()['accessToken']}"
