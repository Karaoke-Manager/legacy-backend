__all__ = ["database", "metadata", "BaseMeta"]

import databases
import ormar
import sqlalchemy

from karman.config import settings

database = databases.Database(settings.db_url)
metadata = sqlalchemy.MetaData()


class BaseMeta(ormar.ModelMeta):
    database = database
    metadata = metadata
