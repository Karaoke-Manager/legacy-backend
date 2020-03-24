from typing import Optional, Union

from flask import Response
from flask_jwt_extended import get_current_user, jwt_required, verify_jwt_in_request
from marshmallow import ValidationError
from werkzeug.exceptions import NotFound

from karman import PermRequired, check_permission_in_request, check_admin_in_request
from karman.models import User, db
from karman.perms import MANAGE_USERS, MANAGE_PERMISSIONS
from karman.rest import api
from karman.rest.resource import RESTResource
from karman.rest.schema import UserSchema, schema


@api.resource('/users')
class UsersResource(RESTResource):

    @PermRequired(MANAGE_USERS)
    @schema(response=UserSchema(many=True))
    def get(self):
        return User.query.all()


@api.resource('/users/<id_or_username>')
class UserResource(RESTResource):

    @staticmethod
    def get_user(id_or_username: Optional[Union[str, int]]) -> User:
        if id_or_username is None:
            verify_jwt_in_request()
            user = get_current_user()
        else:
            try:
                user = User.query.get(int(id_or_username))
            except ValueError:
                user = User.query.filter_by(username=id_or_username).first()
        return user

    @jwt_required
    @schema(response=UserSchema)
    def get(self, id_or_username=None):
        user = self.get_user(id_or_username)
        if user and get_current_user() == user:
            return user
        check_permission_in_request(MANAGE_USERS)
        if user:
            return user
        else:
            raise NotFound

    @jwt_required
    @schema(UserSchema)
    def put(self, data, id_or_username=None):
        # TODO: Make PUT compliant
        user = self.get_user(id_or_username)
        if "user_perms" in data:
            check_permission_in_request(MANAGE_PERMISSIONS)
            user.user_perms = data["user_perms"]
            if len(user.user_perms) != len(data["user_perms"]):
                raise ValidationError("invalid perm names", "userPerms")
        if "is_admin" in data:
            check_admin_in_request()
            if user == get_current_user() and not data["is_admin"]:
                raise ValidationError("cannot revoke own admin status", "admin")
            user.is_admin = data["is_admin"]
        db.session.commit()
        return Response(status=200)
