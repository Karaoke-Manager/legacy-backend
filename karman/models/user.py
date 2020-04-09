from typing import List, Set

from pydantic import root_validator

from karman.helpers.crypto import hash_password
from motor_odm import Document

__all__ = ["User", "Role", "Scope"]

Scope = str


class Role(Document):
    class Mongo:
        collection = "roles"

    name: str
    scopes: Set[Scope] = []

    def __hash__(self):
        return self.name.__hash__()


class User(Document):
    class Mongo:
        collection = "users"

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
