__all__ = ["get_engine", "session"]

from functools import lru_cache
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from karman.settings import Settings


@lru_cache
def get_engine() -> AsyncEngine:
    """
    Returns the SQLAlchemy database engine used by the app.
    """
    settings = Settings.instance()
    return create_async_engine(settings.db_url)


async def session() -> AsyncGenerator[AsyncSession, None]:
    """
    This function is intended to be used as a FastAPI dependency.

    As a dependency this function provides a database session (transaction) that can be
    used to read or write data from or to the database. The session will **not**
    automatically be committed or rolled back.
    """
    async with AsyncSession(get_engine(), expire_on_commit=False) as async_session:
        yield async_session
