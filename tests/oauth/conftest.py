import uuid
from datetime import datetime, timedelta
from typing import Generator

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.monkeypatch import MonkeyPatch

from karman.models import User
from karman.oauth import Scope, Scopes
from karman.settings import Settings


@pytest.fixture
def jwt_secret_key() -> str:
    """Returns the secret Key used for signing JWTs."""
    return "jpRBfXaKi1Rj0CTunObUPym4COeTHQeVt/9bppSQBR0wsk4HLzkvHf8BkoB1OY"


def client_id(request: FixtureRequest) -> str:
    """Returns the client ID."""
    return "test client"


@pytest.fixture
def settings(
    monkeypatch: MonkeyPatch, jwt_secret_key: str
) -> Generator[Settings, None, None]:
    """
    Sets up and returns the ``Settings`` instance.

    This fixture makes sure that the settings are setup according to the current test
    environment.
    """
    instance = Settings(jwt_secret_key=jwt_secret_key)
    monkeypatch.setattr(Settings, "instance", lambda: instance)
    yield instance
    monkeypatch.undo()


@pytest.fixture(params=[(42, "somebody"), (1, "test")])
def user(request: FixtureRequest) -> User:
    """
    Returns a ``User`` instance.

    The user is not necessarily present in the database.
    """
    user = User()
    user.id, user.username = getattr(request, "param")
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
        "jti": token_id,
        "sub": f"user:{user.id}",
        "iat": jwt_token_issue_date,
        "exp": jwt_token_expiry_date,
        "iss": settings.jwt_issuer,
        "username": user.username,
        "extra": "data",
        "client_id": client_id,
        "scope": str(scope),
    }
