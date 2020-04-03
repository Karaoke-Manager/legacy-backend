import jwt
from passlib.context import CryptContext

__all__ = ["hash_password", "verify_password_hash", "create_jwt_token", "verify_jwt_token"]

from ..config import app_config
from ..schemas import TokenPayload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password_hash(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_jwt_token(payload: TokenPayload) -> jwt.PyJWT:
    return jwt.encode(payload.dict(), app_config.jwt.secret_key, algorithm=app_config.jwt.algorithm)


def verify_jwt_token(token: str) -> TokenPayload:
    return TokenPayload(**jwt.decode(token, app_config.jwt.secret_key,
                                     issuer=app_config.jwt.issuer,
                                     algorithms=[app_config.jwt.algorithm]))
