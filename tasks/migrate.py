#!/usr/bin/env python
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from karman.config import app_config
from motor_odm import migrate

MIGRATION_COLLECTION = "migrations"


async def do_migrate(db: AsyncIOMotorDatabase):
    await migrate.create_collections(db)


async def main():
    client = AsyncIOMotorClient(app_config.mongodb)
    db = client.get_default_database()
    await do_migrate(db)


if __name__ == "__main__":
    asyncio.run(main())
