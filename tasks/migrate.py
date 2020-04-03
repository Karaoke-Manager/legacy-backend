#!/usr/bin/env python
import asyncio
import sys
from typing import Type, List, Set

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from karman.config import app_config
from karman.models.base import Migration

MIGRATION_COLLECTION = "migrations"


async def do_migrate(db: AsyncIOMotorDatabase):
    print("Loading Migrations...")
    applied_migrations = {document["name"] async for document in db[MIGRATION_COLLECTION].find()}

    new_migrations: List[Type[Migration]] = []
    # noinspection PyTypeChecker
    remaining_migrations: Set[Type[Migration]] = set(Migration.__subclasses__())
    while len(remaining_migrations) > 0:
        updated = False
        for migration in set(remaining_migrations):
            if migration.name in applied_migrations:
                remaining_migrations.remove(migration)
                continue
            if all(dependency.name in applied_migrations for dependency in migration.dependencies):
                updated = True
                new_migrations.append(migration)
                applied_migrations.add(migration.name)
                remaining_migrations.remove(migration)
        if not updated and len(remaining_migrations) > 0:
            print("Unresolvable dependencies", file=sys.stderr)
            exit(1)

    print(f"Applying {len(new_migrations)} migration(s)")
    for migration in new_migrations:
        print(f"Applying {migration.name}...")
        await migration.execute(db)
        await db[MIGRATION_COLLECTION].insert_one({"name": migration.name})


async def main():
    client = AsyncIOMotorClient(app_config.mongodb)
    db = client.get_default_database()
    await do_migrate(db)


if __name__ == "__main__":
    asyncio.run(main())
