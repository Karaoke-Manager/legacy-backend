from typing import List

from pydantic import BaseModel

__all__ = ["User"]


# class Permission(Validator):
#    def __call__(self, value):
#        if not User.is_perm(value):
#            raise ValidationError("{} is not a valid perm".format(value))

class UserBase(BaseModel):
    username: str
    is_admin: bool
    user_perms: List[str] = []
    # roles = fields.List(fields.Nested(RoleSchema))


class User(UserBase):
    id: int
    all_perms: List[str]

    class Config:
        orm_mode = True
