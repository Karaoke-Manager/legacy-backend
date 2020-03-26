from typing import Optional

from sqlalchemy.orm import Session

from karman import models
from karman.utils import verify_password_hash

__all__ = ["authenticate_user"]


def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    user: Optional[models.User] = db.query(models.User).filter(models.User.username == username).first()
    if user and not verify_password_hash(password, user.password_hash):
        user = None
    return user
