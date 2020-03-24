import json

from flask import Blueprint, current_app
from flask.views import View
from werkzeug.exceptions import HTTPException, NotFound


def resource(self, rule, **options):
    def decorator(fn_or_class):
        if isinstance(fn_or_class, type(View)):
            endpoint = options.pop("endpoint", fn_or_class.__name__)
            fn_or_class.endpoint = endpoint
            self.add_url_rule(rule, view_func=fn_or_class.as_view(endpoint), **options)
            return fn_or_class
        else:
            return self.route(fn_or_class)

    return decorator


Blueprint.resource = resource

api = Blueprint('api', __name__, url_prefix="/v1")


@api.errorhandler(HTTPException)
@api.app_errorhandler(NotFound)
def handle_bad_request(error: HTTPException):
    if error.response:
        return error.response
    cause = getattr(error, 'cause', error)
    data = getattr(error, 'data', {})
    content = {
        "error": {**{
            "code": error.code,
            "type": cause.__class__.__name__,
            "message": error.description
        }, **data}
    }
    return current_app.response_class(
        response=json.dumps(content),
        status=error.code,
    )


from .resource import *
