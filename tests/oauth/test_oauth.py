from calendar import timegm
from datetime import datetime

import pytest
from fastapi.security import SecurityScopes
from jose import jwt
from starlette.status import HTTP_401_UNAUTHORIZED

from karman.exceptions import HTTPException
from karman.models import User
from karman.oauth import (
    Scopes,
    create_access_token,
    get_access_token,
    hash_password,
    verify_password,
)
from karman.settings import Settings


@pytest.mark.parametrize("password", ["", "password", "hello world"])
def test_valid_password_hash(password: str) -> None:
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_invalid_password_hash() -> None:
    hashed = hash_password("password")
    assert verify_password("password 2", hashed) is False


def test_immediate_access_token_claims(
    settings: Settings, user: User, client_id: str, scope: Scopes
) -> None:
    token, claims = create_access_token(user, client_id, scope)
    assert claims.issuer == settings.jwt_issuer
    assert claims.subject == f"user:{user.id}"
    assert claims.username == user.username
    assert claims.scope == scope
    assert claims.client_id == client_id
    assert claims.valid_until - claims.issued_at == settings.jwt_validity_period


def test_create_jwt_access_token(
    settings: Settings, jwt_secret_key: str, user: User, client_id: str, scope: Scopes
) -> None:
    token, claims = create_access_token(user, client_id, scope)
    decoded = jwt.decode(
        token, jwt_secret_key, settings.jwt_algorithm, issuer=settings.jwt_issuer
    )
    expected_claims = claims.dict(encode=True)
    expected_claims["exp"] = timegm(claims.valid_until.utctimetuple())
    expected_claims["iat"] = timegm(claims.issued_at.utctimetuple())
    assert decoded == expected_claims


async def test_get_jwt_access_token(
    settings: Settings,
    jwt_secret_key: str,
    jwt_token_claims: dict,
    user: User,
    client_id: str,
    scope: Scopes,
) -> None:
    token = jwt.encode(
        jwt_token_claims,
        jwt_secret_key,
        settings.jwt_algorithm,
    )
    claims = await get_access_token(SecurityScopes(), token)
    assert claims.subject == f"user:{user.id}"
    assert claims.username == user.username
    assert claims.client_id == client_id
    assert claims.scope == scope


@pytest.mark.parametrize(
    "claim", ["jti", "sub", "iat", "exp", "iss", "client_id", "scope"]
)
async def test_get_access_token_incomplete_claims(
    claim: str,
    settings: Settings,
    jwt_secret_key: str,
    jwt_token_claims: dict,
) -> None:
    del jwt_token_claims[claim]
    token = jwt.encode(jwt_token_claims, jwt_secret_key, settings.jwt_algorithm)
    with pytest.raises(HTTPException) as exc_info:
        await get_access_token(SecurityScopes(), token)
    assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
    assert exc_info.value.error_code == "invalidToken"


async def test_expired_token(
    settings: Settings,
    jwt_secret_key: str,
    jwt_token_claims: dict,
    jwt_token_expiry_date: datetime,
) -> None:
    jwt_token_claims["exp"] = datetime.utcnow() - (
        jwt_token_expiry_date - datetime.utcnow()
    )
    token = jwt.encode(jwt_token_claims, jwt_secret_key, settings.jwt_algorithm)
    with pytest.raises(HTTPException) as exc_info:
        await get_access_token(SecurityScopes(), token)
    assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
    assert exc_info.value.error_code == "tokenExpired"
