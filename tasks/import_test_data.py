import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from karman.config import app_config
from migrate import do_migrate
from tests.data import Dataset


async def main():
    client = AsyncIOMotorClient(app_config.mongodb)
    db = client.get_default_database()
    async with await client.start_session():
        await client.drop_database(db)
        await do_migrate(db)
        await Dataset().load(db)


if __name__ == "__main__":
    asyncio.run(main())
