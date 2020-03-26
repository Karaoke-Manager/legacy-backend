from typing import Optional

from sqlalchemy.orm import Session

from karman.models import User
from karman.utils import verify_password_hash

__all__ = ["authenticate_user"]


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user: Optional[User] = db.query(User).filter_by(username=username).first()
    if user and not verify_password_hash(password, user.password_hash):
        user = None
    return user
