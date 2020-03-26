from datetime import datetime
from typing import List

__all__ = ["TokenPayload", "Token", "BearerToken"]

from karman.schemas.base import BaseSchema


class TokenPayload(BaseSchema):
    sub: str
    exp: datetime
    iss: str
    iat: datetime
    username: str
    scopes: List[str]


class Token(BaseSchema):
    access_token: str
    token_type: str


class BearerToken(Token):
    token_type: str = "bearer"
