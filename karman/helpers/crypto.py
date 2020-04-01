from datetime import datetime, timedelta
from typing import List

import jwt
from passlib.context import CryptContext
from pydantic import validator

__all__ = ["hash_password", "verify_password_hash", "TokenPayload", "create_jwt_token", "verify_jwt_token"]

from ..config import app_config
from ..schemas.base import BaseSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password_hash(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


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


def create_jwt_token(payload: TokenPayload) -> jwt.PyJWT:
    return jwt.encode(payload.dict(), app_config.jwt.secret_key, algorithm=app_config.jwt.algorithm)


def verify_jwt_token(token: str) -> TokenPayload:
    return TokenPayload(**jwt.decode(token, app_config.jwt.secret_key,
                                     issuer=app_config.jwt.issuer,
                                     algorithms=[app_config.jwt.algorithm]))
