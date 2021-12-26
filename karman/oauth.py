from enum import Enum
from functools import lru_cache
from typing import Dict

from fastapi.security import OAuth2PasswordBearer


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

    SONGS = ("songs", "Allow full access to songs.")
    READ_SONGS = ("songs:read", "Allow read access to songs.")
    # TODO: Add more scopes


token_url = "token"
authorize_url = "authorize"

oauth2_password_scheme = OAuth2PasswordBearer(
    scheme_name="Password Login",
    description="Authenticate against the local Karman user database.",
    tokenUrl=f"{token_url}",
    scopes=Scope.all(),
)
