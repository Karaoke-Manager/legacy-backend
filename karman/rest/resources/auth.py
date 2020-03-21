from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource

from karman.models.user import User


class AuthResource(Resource):
    def post(self):
        user = User.Schema().load(request.json)
        # TODO: Verify Password

        access_token = create_access_token(identity=user.username)
        return {"access_token": access_token}, 200
