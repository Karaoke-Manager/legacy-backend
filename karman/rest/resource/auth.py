from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource

from karman.rest.schema import AuthSchema


class AuthResource(Resource):
    def post(self):
        (user, password) = AuthSchema().load(request.json)
        if user and user.validate_password(password):
            access_token = create_access_token(identity=user)
            return {"access_token": access_token}
        else:
            return {"error_message": "username and password did not match"}, 403
