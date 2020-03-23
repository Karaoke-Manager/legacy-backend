from typing import Union

from flask import request, Response
from flask_jwt_extended import get_current_user, jwt_required, verify_jwt_in_request
from flask_restful import Resource, abort
from marshmallow import ValidationError

from karman import PermRequired, check_permission_in_request, check_admin_in_request
from karman.models import User, db
from karman.perms import MANAGE_USERS, MANAGE_PERMISSIONS
from karman.rest.schema import UserSchema


class UsersResource(Resource):
    @PermRequired(MANAGE_USERS)
    def get(self):
        users = User.query.all()
        return UserSchema().dump(users, many=True)


class UserResource(Resource):

    @staticmethod
    def get_user(id_or_username: Union[str, int]) -> User:
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
    def get(self, id_or_username=None):
        user = self.get_user(id_or_username)
        if user and get_current_user() == user:
            return UserSchema().dump(user)
        check_permission_in_request(MANAGE_USERS)
        if user:
            return UserSchema().dump(user)
        else:
            abort(404)

    @jwt_required
    def post(self, id_or_username=None):
        user = self.get_user(id_or_username)
        data = UserSchema().load(request.json)
        if "user_perms" in data:
            check_permission_in_request(MANAGE_PERMISSIONS)
            user.user_perms = data["user_perms"]
            if len(user.user_perms) != len(data["user_perms"]):
                raise ValidationError("invalid perm names", "user_perms")
        if "is_admin" in data:
            check_admin_in_request()
            if user == get_current_user() and not data["is_admin"]:
                raise ValidationError("cannot revoke own admin status", "is_admin")
            user.is_admin = data["is_admin"]
        db.session.commit()
        return Response(status=200)
