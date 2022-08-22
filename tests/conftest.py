from asyncio import AbstractEventLoop, new_event_loop
from typing import AsyncGenerator, Generator

import pytest
from _pytest.monkeypatch import MonkeyPatch
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from karman.db import get_engine
from karman.models import BaseModel
from karman.settings import Settings


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    """
    We override the default ``event_loop`` fixture to be able to use async fixtures with
    a broader scope.
    """
    loop = new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def settings() -> Generator[Settings, None, None]:
    """
    Sets up and returns the ``Settings`` instance.

    This fixture makes sure that the settings are setup according to the current test
    environment.
    """
    monkeypatch = MonkeyPatch()
    instance = Settings(
        # This secret key has no special properties and is used for testing.
        jwt_secret_key="jpRBfXaKi1Rj0CTunObUPym4COeTHQeVt/9bppSQBR0wsk4HLzkvHf8BkoB1OY",
        db_url="sqlite+aiosqlite://",
    )
    monkeypatch.setattr(Settings, "instance", lambda: instance)
    yield instance
    monkeypatch.undo()


@pytest.fixture(scope="session", autouse=True)
async def database(settings: Settings) -> AsyncGenerator[AsyncEngine, None]:
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
        yield engine
        await conn.run_sync(BaseModel.metadata.drop_all)


@pytest.fixture
async def session(database: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(database, expire_on_commit=False) as async_session:
        yield async_session
        await async_session.rollback()
