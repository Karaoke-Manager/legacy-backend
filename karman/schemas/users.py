from typing import Set, List

from karman.models.user import Scope
from karman.schemas.base import ModelSchema, BaseSchema

__all__ = ["User", "Role", "CreateRole", "UpdateRole", "PatchRole"]


class Role(ModelSchema):
    name: str
    scopes: Set[str]


class CreateRole(BaseSchema):
    name: str
    scopes: Set[str] = []


class UpdateRole(BaseSchema):
    id: int = None
    name: str
    scopes: Set[str] = []


class PatchRole(BaseSchema):
    id: int = None
    name: str = None
    scopes: Set[str] = []


class User(ModelSchema):
    username: str
    is_admin: str

    roles: List[Role]
    scopes: Set[Scope]
    all_scopes: Set[Scope]
