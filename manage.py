#!/usr/bin/env python
from typing import Type, List, Set, Tuple, Union

import typer
from pymongo import MongoClient
from pymongo.database import Database

from karman.config import app_config
from karman.models.base import Migration
from tests.data import Dataset

MIGRATION_COLLECTION = "migrations"
app = typer.Typer()


def get_database(client=False) -> Union[Database, Tuple[Database, MongoClient]]:
    client = MongoClient(app_config.mongodb)
    db = client.get_default_database()
    if client:
        return db, client
    else:
        return db


@app.command()
def migrate():
    db = get_database()
    do_migrate(db)


def do_migrate(db: Database):
    typer.secho("Loading Migrations")
    applied_migrations = {document["name"] for document in db[MIGRATION_COLLECTION].find()}

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
            typer.secho("Unresolvable dependencies", err=True)
            print(remaining_migrations)
            exit(1)

    typer.secho(f"Applying {len(new_migrations)} migration(s)")
    with typer.progressbar(new_migrations) as progress:
        for migration in progress:
            print(f"Applying {migration.name}...")
            migration.execute(db)
            db[MIGRATION_COLLECTION].insert_one({"name": migration.name})


@app.command()
def import_test_data():
    db, client = get_database(True)
    with client.start_session():
        client.drop_database(db)
        do_migrate(db)
        Dataset().load(db)


if __name__ == "__main__":
    app()
