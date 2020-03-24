from typing import Set

from sqlalchemy.orm import validates
from sqlalchemy.sql import expression
from werkzeug.security import generate_password_hash, check_password_hash

from alembic_data import register_object, managed_model
from .database import db

__all__ = ["User", "Role", "register_permissions"]


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.Text(), nullable=False, unique=True)
    password_hash = db.Column(db.String(94))
    is_admin = db.Column(db.Boolean(), nullable=False, default=False, server_default=expression.false())

    permissions = db.relationship('Permission', secondary=lambda: user_permissions, lazy=True)
    roles = db.relationship('Role', secondary=lambda: user_roles, back_populates="users", lazy=True)

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


class Role(db.Model):
    name = db.Column(db.Text(), primary_key=True)

    permissions = db.relationship('Permission', secondary=lambda: role_permissions, lazy=False)
    users = db.relationship("User", secondary=lambda: user_roles, back_populates="roles", lazy=True)

    @validates('name')
    def validate_name(self, key, value):
        return value.lower()

    def __repr__(self):
        return '<Role {}>'.format(self.name)

    def __str__(self):
        return self.name


@managed_model
class Permission(db.Model):
    name = db.Column(db.Text(), primary_key=True, unique=True)

    @validates('name')
    def validate_name(self, key, value):
        return value.lower()

    def __repr__(self):
        return '<Permission {}>'.format(self.name)

    def __str__(self):
        return self.name


user_permissions = db.Table('user_permissions',
                            db.Column('user_id', db.Integer(), db.ForeignKey('user.id'), primary_key=True),
                            db.Column('permission_name', db.Integer(), db.ForeignKey('permission.name'),
                                      primary_key=True))
user_roles = db.Table('user_roles',
                      db.Column('user_id', db.Integer(), db.ForeignKey('user.id'), primary_key=True),
                      db.Column('role_name', db.Integer(), db.ForeignKey('role.name'), primary_key=True))
role_permissions = db.Table('role_permissions',
                            db.Column('role_name', db.Integer, db.ForeignKey('role.name'), primary_key=True),
                            db.Column('permission_name', db.Integer, db.ForeignKey('permission.name'),
                                      primary_key=True))


def register_permissions(*names: str):
    for name in names:
        register_object(Permission, name=name)
