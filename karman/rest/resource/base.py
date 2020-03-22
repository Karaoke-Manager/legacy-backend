from flask_restful import Resource
from marshmallow import ValidationError

from karman.rest.api import api


class RESTResource(Resource):
    def dispatch_request(self, *args, **kwargs):
        try:
            return super().dispatch_request(*args, **kwargs)
        except ValidationError as error:
            return api.make_response({"errors": error.messages}, 400)
