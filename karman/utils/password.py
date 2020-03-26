from passlib.context import CryptContext

__all__ = ["hash_password", "verify_password_hash"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password_hash(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)
