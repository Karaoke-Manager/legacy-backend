from datetime import datetime, timedelta
from typing import List

from pydantic import validator

from karman.config import app_config
from karman.schemas.base import BaseSchema

__all__ = ["Token", "BearerToken", "TokenPayload"]


class Token(BaseSchema):
    access_token: str
    token_type: str


class BearerToken(Token):
    token_type: str = "bearer"


class TokenPayload(BaseSchema):
    sub: str = None
    exp: datetime = None
    iss: str = app_config.jwt.issuer
    iat: datetime = None
    username: str
    scopes: List[str] = []

    @validator('sub', pre=True, always=True)
    def default_sub(cls, sub, *, values: dict, **kwargs):
        return sub or f"username:{values.get('username')}"

    @validator("exp", pre=True, always=True)
    def default_exp(cls, exp):
        return exp or datetime.utcnow() + timedelta(minutes=app_config.jwt.access_token_expire_minutes)

    @validator("iat", pre=True, always=True)
    def default_iat(cls, iat):
        return iat or datetime.utcnow()
