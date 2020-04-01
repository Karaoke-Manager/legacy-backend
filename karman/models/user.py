from typing import List, Set

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import validator, root_validator
from pymongo import ASCENDING
from pymongo.database import Database

from karman.helpers.crypto import hash_password
from .base import Document, Migration

__all__ = ["User", "Role"]

Scope = str


class Role(Document):
    class UniqueNameMigration(Migration):
        name = "role-unique-index"

        @classmethod
        def execute(cls, db: Database):
            db.roles.create_index([("name", ASCENDING)], unique=True)

    __collection__ = "role"
    name: str
    scopes: Set[Scope] = []

    @validator('name')
    def validate_name(cls, value):
        return value.lower()

    def __hash__(self):
        return self.name.__hash__()


class User(Document):
    class UniqueNameMigration(Migration):
        name = "user-unique-index"

        @classmethod
        def execute(cls, db: Database):
            db.users.create_index([("name", ASCENDING)], unique=True)

    __collection__ = "user"
    username: str
    password_hash: str
    is_admin: bool = False

    scopes: Set[Scope] = []
    roles: List[Role] = []

    @root_validator(pre=True)
    def init_password(cls, values):
        if "password" in values and "password_hash" not in values:
            values["password_hash"] = hash_password(values["password"])
        return values

    @property
    def password(self):
        raise AttributeError("password is not a readable property")

    @password.setter
    def password(self, password: str):
        self.password_hash = hash_password(password)

    @property
    def all_scopes(self) -> Set[Scope]:
        return self.scopes | {scope for role in self.roles for scope in role.scopes}

    def __hash__(self):
        return self.username.__hash__()

    @classmethod
    async def get_by_username(cls, db: AsyncIOMotorDatabase, username: str):
        return cls(**await cls.collection(db).find_one({"username": username}))
