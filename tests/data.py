import asyncio

from motor.motor_asyncio import AsyncIOMotorDatabase

from karman.models import Role, User
from karman.scopes import MANAGE_LIBRARY


class Dataset:
    UNUSED_USERNAME = "absent"
    UNUSED_ROLE = "absent"
    ADMIN_PASSWORD = "password"

    def __init__(self):
        self.manager_role = Role(name="Manager", scopes={MANAGE_LIBRARY})

        self.admin = User(username="admin", password=Dataset.ADMIN_PASSWORD, is_admin=True)
        self.users = [
            User(username="user1", password="password1"),
            User(username="user2", password="password1", roles={self.manager_role})
        ]

    async def user_count(self, db: AsyncIOMotorDatabase):
        return await db.users.count()

    async def load(self, db: AsyncIOMotorDatabase):
        await asyncio.gather(
            self.manager_role.insert(db),
            User.batch_create(db, self.admin, *self.users)
        )
