__all__ = ["Token", "BearerToken"]

from karman.schemas.base import BaseSchema


class Token(BaseSchema):
    access_token: str
    token_type: str


class BearerToken(Token):
    token_type: str = "bearer"
