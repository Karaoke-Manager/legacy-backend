from functools import lru_cache
from typing import Generator

import pytest
from _pytest.monkeypatch import MonkeyPatch

from karman.models import User
from karman.oauth import (
    Scope,
    Scopes,
    create_access_token,
    hash_password,
    verify_password,
)
from karman.settings import Settings

JWT_KEY = "jpRBfXaKi1Rj0CTunObUPym4COeTHQeVt/9bppSQBR0wsk4HLzkvHf8BkoB1OY"


@pytest.fixture
def settings(monkeypatch: MonkeyPatch) -> Generator[None, None, None]:
    @lru_cache
    def impl() -> Settings:
        return Settings(jwt_secret_key=JWT_KEY)

    monkeypatch.setattr(Settings, "instance", impl)
    yield
    monkeypatch.undo()


@pytest.mark.parametrize("password", ["", "password", "hello world"])
def test_valid_password_hash(password: str) -> None:
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_invalid_password_hash() -> None:
    hashed = hash_password("password")
    assert verify_password("password 2", hashed) is False


@pytest.mark.usefixtures("settings")
def test_immediate_access_token_claims() -> None:
    user = User()
    user.id = 42
    user.username = "somebody"
    scope = Scopes({Scope.SONGS})
    client_id = "test"
    token, claims = create_access_token(user, client_id, scope)
    assert claims.subject == "user:42"
    assert claims.username == "somebody"
    assert claims.scope == Scopes({Scope.SONGS})
    assert claims.client_id == "test"
