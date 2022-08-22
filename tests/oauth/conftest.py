import uuid
from datetime import datetime, timedelta

import pytest
from _pytest.fixtures import FixtureRequest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from karman import get_app
from karman.models import User
from karman.oauth import Scope, Scopes, hash_password
from karman.settings import Settings


@pytest.fixture
def client_id(request: FixtureRequest) -> str:
    """Returns the client ID."""
    return "test client"


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    """Returns a fully configured instance of the app to be tested."""
    return get_app()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Returns a test client that can be used to issue requests to the app."""
    return TestClient(app)


@pytest.fixture(params=[(42, "somebody", "my password"), (1, "test", "pass12§421")])
def user(request: FixtureRequest) -> User:
    """
    Returns a ``User`` instance.

    The user is not necessarily present in the database.
    """
    user = User()
    uid, username, password = getattr(request, "param")
    user.id, user.username = uid, username
    setattr(user, "cleartext_password", password)
    user.password = hash_password(password)
    return user


@pytest.fixture
async def user_in_db(user: User, session: AsyncSession) -> User:
    session.add(user)
    await session.flush()
    return user


@pytest.fixture(params=[{Scope.SONGS, Scope.READ_SONGS}, {Scope.ALL}, {}])
def scope(request: FixtureRequest) -> Scopes:
    """
    Returns a valid ``Scopes`` instance.
    """
    return Scopes(getattr(request, "param"))


@pytest.fixture(
    params=[
        timedelta(),
        timedelta(minutes=30),
        timedelta(hours=2),
    ]
)
def jwt_token_issue_date(request: FixtureRequest) -> datetime:
    """Returns a ``datetime`` object to be used as a JWT issue date."""
    offset: timedelta = getattr(request, "param")
    return datetime.utcnow() - offset


@pytest.fixture(
    params=[
        timedelta(hours=2),
        timedelta(minutes=25),
        timedelta(seconds=30),
    ]
)
def jwt_token_expiry_date(request: FixtureRequest) -> datetime:
    """
    Returns a ``datetime`` object to be used as a JWT expiry date.

    The date is guaranteed to be in the future.
    """
    offset: timedelta = getattr(request, "param")
    return datetime.utcnow() + offset


@pytest.fixture
def jwt_token_claims(
    settings: Settings,
    user: User,
    client_id: str,
    scope: Scopes,
    jwt_token_issue_date: datetime,
    jwt_token_expiry_date: datetime,
) -> dict:
    """
    Returns a dictionary of JWT claims. This can almost be regarded as a test token.
    """
    token_id = str(uuid.uuid4())
    return {
        "iss": settings.jwt_issuer,
        "jti": token_id,
        "sub": f"user:{user.id}",
        "iat": jwt_token_issue_date,
        "exp": jwt_token_expiry_date,
        "username": user.username,
        "client_id": client_id,
        "scope": str(scope),
        "extra": "data",
    }
