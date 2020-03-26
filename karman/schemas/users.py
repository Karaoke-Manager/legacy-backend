from typing import Set, List, Optional

from pydantic import validator

from karman.schemas.base import ModelSchema, BaseSchema

__all__ = ["User", "Role", "CreateRole", "UpdateRole", "PatchRole"]


class Role(ModelSchema):
    id: int
    name: str
    scopes: Set[str]


class CreateRole(BaseSchema):
    name: str
    scopes: Set[str] = []


class UpdateRole(BaseSchema):
    id: Optional[int]
    name: str
    scopes: Set[str] = []


class PatchRole(BaseSchema):
    id: Optional[int]
    name: Optional[str]
    scopes: Set[str] = []


class User(ModelSchema):
    id: int
    username: str
    is_admin: str

    roles: List[Role]
    scopes: Set[str]
    all_scopes: Set[str]

    @validator("roles", each_item=True)
    def validate_roles(cls, role: Role):
        return role.name
