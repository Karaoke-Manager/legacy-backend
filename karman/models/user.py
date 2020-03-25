from typing import Set

from sqlalchemy import Column, Integer, Text, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.sql import expression
from werkzeug.security import generate_password_hash, check_password_hash

from alembic_data import register_object, managed_model
from .base import Model

__all__ = ["User", "Role", "register_permissions"]


class User(Model):
    __tablename__ = "user"

    id = Column(Integer(), primary_key=True)
    username = Column(Text(), nullable=False, unique=True)
    password_hash = Column(String(94))
    is_admin = Column(Boolean(), nullable=False, default=False, server_default=expression.false())

    permissions = relationship('Permission', secondary=lambda: user_permissions, lazy=True)
    roles = relationship('Role', secondary=lambda: user_roles, back_populates="users", lazy=True)

    def __init__(self, **kwargs):
        password = kwargs.pop("password", None)
        perms = kwargs.pop("perms", [])
        super().__init__(**kwargs)
        if password:
            self.set_password(password)
        if perms:
            self.add_perms(*perms)

    def set_password(self, password: str) -> str:
        hashed = generate_password_hash(password)
        self.password_hash = hashed
        return hashed

    def validate_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def all_roles(self, as_objects=False):
        if as_objects:
            return self.roles
        else:
            return [role.name for role in self.roles]

    @property
    def user_perms(self) -> Set[str]:
        return set([permission.name for permission in self.permissions])

    @user_perms.setter
    def user_perms(self, perms: Set[str]):
        self.permissions = list(Permission.query.filter(Permission.name.in_(perms)))

    @property
    def role_perms(self) -> Set[str]:
        return set([permission.name for role in self.roles for permission in role.permissions])

    @property
    def all_perms(self) -> Set[str]:
        return self.user_perms | self.role_perms

    def has_perms(self, *perms) -> bool:
        return self.is_admin or all(perm in self.all_perms for perm in perms)

    @classmethod
    def is_perm(cls, perm):
        return Permission.query.get(perm) is not None

    can = has_perms

    def add_perms(self, *perms):
        for perm in perms:
            if perm not in self.user_perms:
                permission = Permission.query.get(perm)
                if permission is None:
                    pass  # FIXME: Raise error?
                self.permissions.append(Permission.query.get(perm))

    def remove_perms(self, *perms):
        self.permissions = [permission for permission in self.permissions if permission.name not in perms]

    def clear_perms(self):
        self.permissions = []

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def __str__(self):
        return self.username


class Role(Model):
    __tablename__ = "role"

    name = Column(Text(), primary_key=True)

    permissions = relationship('Permission', secondary=lambda: role_permissions, lazy=False)
    users = relationship("User", secondary=lambda: user_roles, back_populates="roles", lazy=True)

    @validates('name')
    def validate_name(self, key, value):
        return value.lower()

    def __repr__(self):
        return '<Role {}>'.format(self.name)

    def __str__(self):
        return self.name


@managed_model
class Permission(Model):
    __tablename__ = "permission"

    name = Column(Text(), primary_key=True, unique=True)

    @validates('name')
    def validate_name(self, key, value):
        return value.lower()

    def __repr__(self):
        return '<Permission {}>'.format(self.name)

    def __str__(self):
        return self.name


# noinspection PyTypeChecker
user_permissions = Table('user_permissions', Model.metadata,
                         Column('user_id', Integer(), ForeignKey('user.id'), primary_key=True),
                         Column('permission_name', Integer(), ForeignKey('permission.name'),
                                primary_key=True))
# noinspection PyTypeChecker
user_roles = Table('user_roles', Model.metadata,
                   Column('user_id', Integer(), ForeignKey('user.id'), primary_key=True),
                   Column('role_name', Integer(), ForeignKey('role.name'), primary_key=True))
# noinspection PyTypeChecker
role_permissions = Table('role_permissions', Model.metadata,
                         Column('role_name', Integer(), ForeignKey('role.name'), primary_key=True),
                         Column('permission_name', Integer, ForeignKey('permission.name'),
                                primary_key=True))


def register_permissions(*names: str):
    for name in names:
        register_object(Permission, name=name)
