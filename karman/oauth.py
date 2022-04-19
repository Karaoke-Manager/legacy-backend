from enum import Enum
from functools import lru_cache
from typing import Dict, Optional, TypeAlias

from fastapi import HTTPException, Request
from fastapi.openapi.models import (
    OAuthFlowAuthorizationCode,
    OAuthFlowPassword,
    OAuthFlows,
)
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from starlette.status import HTTP_401_UNAUTHORIZED

OAuth2Token: TypeAlias = str


class Scope(str, Enum):
    @classmethod
    @lru_cache
    def all(cls) -> Dict[str, str]:
        return {scope.value: scope.description for scope in Scope}

    # Include this to help mypy detect the description field
    description: str

    def __new__(cls, value: str, description: str = "") -> "Scope":
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    def __repr__(self):
        return f"{self.__class__.__name__}.{self._name_}"

    SONGS = ("songs", "Allow full access to songs.")
    READ_SONGS = ("songs:read", "Allow read access to songs.")
    # TODO: Add more scopes


token_url = "token"
authorize_url = "authorize"


class OAuth2Bearer(OAuth2):
    async def __call__(self, request: Request) -> Optional[OAuth2Token]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


# TODO: Allow configuration of enabled flows?
oauth_flows = OAuthFlows(
    password=OAuthFlowPassword(tokenUrl=token_url, scopes=Scope.all()),
    authorizationCode=OAuthFlowAuthorizationCode(
        tokenUrl=token_url, authorizationUrl=authorize_url, scopes=Scope.all()
    ),
)

get_token = OAuth2Bearer(
    scheme_name="OAuth 2",
    description="Authenticate using one of the OAuth 2 flows.",
    flows=oauth_flows,
)
