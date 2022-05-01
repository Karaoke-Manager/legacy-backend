from calendar import timegm
from datetime import datetime

import pytest
from fastapi.security import SecurityScopes
from jose import jwt
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_405_METHOD_NOT_ALLOWED,
)
from starlette.testclient import TestClient

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
    settings: Settings, user: User, client_id: str, scope: Scopes
) -> None:
    token, claims = create_access_token(user, client_id, scope)
    decoded = jwt.decode(
        token,
        settings.jwt_secret_key,
        settings.jwt_algorithm,
        issuer=settings.jwt_issuer,
    )
    expected_claims = claims.dict(encode=True)
    expected_claims["exp"] = timegm(claims.valid_until.utctimetuple())
    expected_claims["iat"] = timegm(claims.issued_at.utctimetuple())
    assert decoded == expected_claims


async def test_get_jwt_access_token(
    settings: Settings,
    jwt_token_claims: dict,
    user: User,
    client_id: str,
    scope: Scopes,
) -> None:
    token = jwt.encode(
        jwt_token_claims,
        settings.jwt_secret_key,
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
    jwt_token_claims: dict,
) -> None:
    del jwt_token_claims[claim]
    token = jwt.encode(
        jwt_token_claims, settings.jwt_secret_key, settings.jwt_algorithm
    )
    with pytest.raises(HTTPException) as exc_info:
        await get_access_token(SecurityScopes(), token)
    assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
    assert exc_info.value.error_code == "invalidToken"


async def test_expired_token(
    settings: Settings,
    jwt_token_claims: dict,
    jwt_token_expiry_date: datetime,
) -> None:
    jwt_token_claims["exp"] = datetime.utcnow() - (
        jwt_token_expiry_date - datetime.utcnow()
    )
    token = jwt.encode(
        jwt_token_claims, settings.jwt_secret_key, settings.jwt_algorithm
    )
    with pytest.raises(HTTPException) as exc_info:
        await get_access_token(SecurityScopes(), token)
    assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
    assert exc_info.value.error_code == "tokenExpired"


@pytest.mark.parametrize("method", ["GET", "PUT", "PATCH", "HEAD"])
def test_token_endpoint_invalid_method(method: str, client: TestClient) -> None:
    response = client.request(method, "/v1/token")
    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    if method == "HEAD":
        assert response.content == b""
    else:
        body: dict = response.json()
        assert body.keys() >= {"code", "message"}
        assert body["code"] == "methodNotAllowed"


def test_token_endpoint_missing_grant_type(client: TestClient) -> None:
    response = client.post("/v1/token")
    body: dict = response.json()
    assert body.keys() >= {"error", "error_description"}
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert body["error"] == "invalid_request"


@pytest.mark.parametrize("grant_type", ["pass", "123"])
def test_token_endpoint_invalid_grant_type(grant_type: str, client: TestClient) -> None:
    response = client.post("/v1/token", data={"grant_type": grant_type})
    body: dict = response.json()
    assert body.keys() >= {"error", "error_description"}
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert body["error"] == "unsupported_grant_type"


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"grant_type": "password"},
        {"grant_type": "password", "username": "user"},
        {"grant_type": "password", "password": "pass"},
    ],
)
def test_token_endpoint_missing_parameters(params: dict, client: TestClient) -> None:
    response = client.post("/v1/token", data=params)
    body: dict = response.json()
    assert body.keys() >= {"error", "error_description"}
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert body["error"] == "invalid_request"


def test_token_endpoint_missing_password(client: TestClient) -> None:
    response = client.post(
        "/v1/token", data={"grant_type": "password", "username": "user"}
    )
    body: dict = response.json()
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert body["error"] == "invalid_request"


@pytest.mark.parametrize("username,password", [("some", "body"), ("absent", "user")])
def test_token_endpoint_invalid_password(
    username: str, password: str, client: TestClient
) -> None:
    response = client.post(
        "/v1/token",
        data={"grant_type": "password", "username": username, "password": password},
    )
    body: dict = response.json()
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert body["error"] == "invalid_request"


async def test_token_endpoint_valid_password(
    user_in_db: User, settings: Settings, client: TestClient
) -> None:
    password = getattr(user_in_db, "cleartext_password")
    response = client.post(
        "/v1/token",
        data={
            "grant_type": "password",
            "username": user_in_db.username,
            "password": password,
        },
    )
    body: dict = response.json()
    assert body.keys() >= {"access_token", "expires_in", "scope", "token_type"}
    assert body["token_type"] == "Bearer"
    assert body["expires_in"] == settings.jwt_validity_period.seconds
    # TODO: Validate Scope
    token = jwt.decode(
        body["access_token"],
        settings.jwt_secret_key,
        settings.jwt_algorithm,
        issuer=settings.jwt_issuer,
        options={
            "require_jti": True,
            "require_iss": True,
            "require_sub": True,
            "require_iat": True,
            "require_exp": True,
            "require_client_id": True,
            "require_scope": True,
        },
    )
    assert token is not None
