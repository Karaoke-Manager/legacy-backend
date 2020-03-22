from flask_jwt_extended import JWTManager

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
    # TODO: Add Roles/Permissions
    return None

# TODO: Possibly check for deactivated or deleted users
# @jwt.user_loader_error_loader
# def custom_user_loader_error(identity):
#    ret = {
#        "msg": "User {} not found".format(identity)
#    }
#    return jsonify(ret), 404
