from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from karman import models
from karman.helpers.crypto import verify_password_hash

__all__ = ["authenticate_user"]


async def authenticate_user(db: AsyncIOMotorDatabase, username: str, password: str) -> Optional[models.User]:
    user: Optional[models.User] = await models.User.get_by_username(db, username)
    if user and not verify_password_hash(password, user.password_hash):
        user = None
    return user
