from flask import Blueprint
from flask_restful import Api

from karman.rest.resource import *

api = Api()
rest_api = Blueprint('rest_api', __name__)

api.add_resource(AuthResource, '/login', endpoint="login")
api.add_resource(UsersResource, '/users', endpoint="users")
api.add_resource(UserResource, '/users/<id_or_username>', endpoint="user")
rest_api.add_url_rule('/me', endpoint="user")
api.add_resource(SongResource, '/songs/<int:id>')


@rest_api.errorhandler(ValidationError)
def handle_validation_error(error: ValidationError):
    return api.make_response({
        "errors": {
            error.field_name: error.messages
        }
    }, 400)


api.init_app(rest_api)
