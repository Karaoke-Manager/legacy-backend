from typing import Optional

from karman import models
from karman.helpers.crypto import verify_password_hash

__all__ = ["authenticate_user"]

from motor_odm import q


async def authenticate_user(username: str, password: str) -> Optional[models.User]:
    user: Optional[models.User] = await models.User.find_one(q(username=username))
    if user and not verify_password_hash(password, user.password_hash):
        user = None
    return user
