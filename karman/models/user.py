from typing import Collection, List, Set

from sqlalchemy import Column, Integer, Text, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.sql import expression

from alembic_data import managed_model
from .base import Model
from ..scopes import all_scopes
from ..utils.password import hash_password

__all__ = ["User", "Role", "Scope"]


class User(Model):
    __tablename__ = "user"

    id: int = Column(Integer(), primary_key=True)
    username: str = Column(Text(), nullable=False, unique=True)
    password_hash: str = Column(String(94))
    is_admin: bool = Column(Boolean(), nullable=False, default=False, server_default=expression.false())

    scopes: List["Scope"] = relationship('Scope', secondary=lambda: user_scopes, lazy=True)
    roles: List["Role"] = relationship('Role', secondary=lambda: user_roles, back_populates="users", lazy=True)

    def __init__(self, **kwargs):
        password = kwargs.pop("password", None)
        super().__init__(**kwargs)
        if password:
            self.set_password(password)

    def set_password(self, password: str) -> str:
        self.password_hash = hash_password(password)
        return self.password_hash

    @property
    def user_scopes(self) -> Set[str]:
        return set([scope.name for scope in self.scopes])

    @user_scopes.setter
    def user_scopes(self, scopes: Collection[str]):
        self.scopes = [Scope(name=scope) for scope in scopes if scope in all_scopes]

    @property
    def role_scopes(self) -> Set[str]:
        return set([scope.name for role in self.roles for scope in role.scopes])

    @property
    def all_scopes(self) -> Set[str]:
        return self.user_scopes | self.role_scopes

    def has_scope(self, *scopes) -> bool:
        return self.is_admin or all(scope in self.all_scopes for scope in scopes)

    def add_scopes(self, *scopes):
        for scope in scopes:
            if scope in all_scopes:
                if scope not in self.user_scopes:
                    self.scopes.append(Scope(name=scope))
            else:
                raise ValueError

    def remove_scopes(self, *scopes):
        self.scopes = [scope for scope in self.scopes if scope.name not in scopes]

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def __str__(self):
        return self.username


class Role(Model):
    __tablename__ = "role"

    name = Column(Text(), primary_key=True)

    scopes = relationship('Scope', secondary=lambda: role_scopes, lazy=False)
    users = relationship("User", secondary=lambda: user_roles, back_populates="roles", lazy=True)

    @validates('name')
    def validate_name(self, key, value):
        return value.lower()

    def __repr__(self):
        return '<Role {}>'.format(self.name)

    def __str__(self):
        return self.name


@managed_model
class Scope(Model):
    __tablename__ = "scope"

    name = Column(Text(), primary_key=True, unique=True)

    @validates('name')
    def validate_name(self, key, value):
        return value.lower()

    def __repr__(self):
        return '<Scope {}>'.format(self.name)

    def __str__(self):
        return self.name


user_scopes = Table('user_scopes', Model.metadata,
                    Column('user_id', Integer(), ForeignKey('user.id'), primary_key=True),
                    Column('scope_name', Integer(), ForeignKey('scope.name'),
                           primary_key=True))
user_roles = Table('user_roles', Model.metadata,
                   Column('user_id', Integer(), ForeignKey('user.id'), primary_key=True),
                   Column('role_name', Integer(), ForeignKey('role.name'), primary_key=True))
role_scopes = Table('role_scopes', Model.metadata,
                    Column('role_name', Integer(), ForeignKey('role.name'), primary_key=True),
                    Column('scope_name', Integer, ForeignKey('scope.name'),
                           primary_key=True))
