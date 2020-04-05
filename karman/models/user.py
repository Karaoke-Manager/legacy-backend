from typing import List, Set

from pydantic import root_validator
from pymongo import ASCENDING

from karman.helpers.crypto import hash_password

__all__ = ["User", "Role", "Scope"]

from motor_odm import Document

Scope = str


class Role(Document):
    class Meta:
        collection = "roles"
        validate = True
        indexes = [
            ([("name", ASCENDING)], {"unique": True})
        ]

    name: str
    scopes: Set[Scope] = []

    def __hash__(self):
        return self.name.__hash__()


class User(Document):
    class Meta:
        collection = "users"
        validate = True
        indexes = [
            ([("username", ASCENDING)], {"unique": True})
        ]

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
        return self.scopes.union(*(role.scopes for role in self.roles))

    def __hash__(self):
        return self.username.__hash__()

    @classmethod
    async def get_by_username(cls, username: str):
        document = await cls.collection().find_one({"username": username})
        return cls(**document) if document else None
