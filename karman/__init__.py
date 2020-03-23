from functools import wraps

from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims
from flask_restful import abort

from karman.models import User

jwt = JWTManager()


@jwt.user_identity_loader
def user_identity_lookup(identity: User):
    return identity.username


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    return User.query.filter_by(username=identity).first()


@jwt.user_claims_loader
def add_claims_to_access_token(user: User):
    return {
        "admin": user.is_admin,
        "permissions": list(user.all_perms)
    }


def check_permission_in_request(perm: str):
    verify_jwt_in_request()
    claims = get_jwt_claims()
    if not claims['admin'] and perm not in claims['permissions']:
        abort(403)


def check_admin_in_request():
    verify_jwt_in_request()
    claims = get_jwt_claims()
    if not claims['admin']:
        # TODO: Unify errors somehow
        return {
                   "errors": [
                       "you must be admin to perform this action"
                   ]
               }, 403


class PermRequired:
    def __init__(self, perm):
        self.perm = perm

    def __call__(self, fn, *args, **kwargs):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            check_permission_in_request(self.perm)
            return fn(*args, **kwargs)

        return wrapper


class AdminRequired:
    def __init__(self):
        pass

    def __call__(self, fn, *args, **kwargs):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            check_admin_in_request()
            return fn(*args, **kwargs)

        return wrapper
