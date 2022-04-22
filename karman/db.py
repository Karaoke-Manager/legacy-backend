from functools import lru_cache
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from karman.settings import Settings


@lru_cache
def get_engine() -> AsyncEngine:
    settings = Settings.instance()
    return create_async_engine(settings.db_url)


async def session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(get_engine(), expire_on_commit=False) as async_session:
        yield async_session
