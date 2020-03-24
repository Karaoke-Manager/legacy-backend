from flask_jwt_extended import create_access_token
from werkzeug.exceptions import Forbidden

from karman.rest import api
from karman.rest.resource.base import RESTResource
from karman.rest.schema import AuthSchema, schema


@api.resource("/login")
class AuthResource(RESTResource):

    @schema(AuthSchema)
    def post(self, data):
        user = data["user"]
        password = data["password"]
        if user and user.validate_password(password):
            access_token = create_access_token(identity=user)
            return {
                "access_token": access_token
            }
        else:
            raise Forbidden("username and password did not match")
