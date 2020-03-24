import json

from flask import current_app
from flask.views import MethodView
from werkzeug.wrappers import BaseResponse


class RESTResource(MethodView):
    def dispatch_request(self, *args, **kwargs):
        data = super().dispatch_request(*args, **kwargs)
        response = self.make_response(data)
        return response

    # TODO: Chunked Encoded Response for Lists?
    def make_response(self, data):
        if data is None:
            response: BaseResponse = current_app.make_response((None, 204))
            del response.headers['Content-Type']
            return response
        elif isinstance(data, current_app.response_class):
            return data
        else:
            return current_app.response_class(
                response=json.dumps(data),
                status=200,
                content_type="application/json"
            )
