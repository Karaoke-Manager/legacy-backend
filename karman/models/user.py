import json
from typing import Collection, List, FrozenSet

from sqlalchemy import Column, Integer, Text, String, Boolean, Table, ForeignKey, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates, relationship
from sqlalchemy.sql import expression

from .base import Model
from ..scopes import all_scopes
from ..utils.password import hash_password

__all__ = ["User", "Role"]


class Role(Model):
    __tablename__ = "role"

    id: int = Column(Integer(), primary_key=True)
    name: str = Column(Text(), unique=True)
    _scopes: str = Column("scopes", Text())

    users: List["User"] = relationship("User", secondary=lambda: user_roles, back_populates="roles", lazy=True)

    def __init__(self, scopes=None, **kwargs):
        super().__init__(**kwargs)
        self.scopes = scopes if scopes else []

    @validates('name')
    def validate_name(self, key, value):
        return value.lower()

    @hybrid_property
    def scopes(self) -> FrozenSet[str]:
        return frozenset(json.loads(self._scopes))

    @scopes.setter
    def scopes(self, scopes: Collection[str]):
        for scope in scopes:
            if scope not in all_scopes:
                raise ValueError
        self._scopes = json.dumps(list(scopes))

    @scopes.expression
    def scopes(cls):
        return cls._scopes.split(',')

    def __repr__(self):
        return '<Role {}>'.format(self.name)

    def __str__(self):
        return self.name


class User(Model):
    __tablename__ = "user"

    id: int = Column(Integer(), primary_key=True)
    username: str = Column(Text(), nullable=False, unique=True)
    password_hash: str = Column(String(94))
    is_admin: bool = Column(Boolean(), nullable=False, default=False, server_default=expression.false())

    _scopes: str = Column("scopes", Text())
    roles: List[Role] = relationship('Role', secondary=lambda: user_roles, back_populates="users", lazy=True)

    def __init__(self, password: str = None, scopes: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        if password:
            self.password = password
        self.scopes = scopes if scopes else []

    @property
    def password(self):
        raise AttributeError("password is not a readable property")

    @password.setter
    def password(self, password: str):
        self.password_hash = hash_password(password)

    @hybrid_property
    def scopes(self) -> FrozenSet[str]:
        return frozenset(json.loads(self._scopes))

    @scopes.setter
    def scopes(self, scopes: Collection[str]):
        for scope in scopes:
            if scope not in all_scopes:
                raise ValueError
        self._scopes = json.dumps(list(scopes))

    @scopes.expression
    def scopes(cls):
        return func.string_split(cls._scopes, ',')

    @property
    def all_scopes(self) -> FrozenSet[str]:
        scopes = set(self.scopes)
        for role in self.roles:
            scopes.update(role.scopes)
        return frozenset(scopes)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def __str__(self):
        return self.username


user_roles = Table('user_roles', Model.metadata,
                   Column('user_id', Integer(), ForeignKey('user.id'), primary_key=True),
                   Column('role_id', Integer(), ForeignKey('role.id'), primary_key=True))
