from typing import Union, Type

from flask import request as current_request, Response
from marshmallow import Schema, ValidationError
from werkzeug.exceptions import BadRequest

from .auth import AuthSchema
from .user import UserSchema


def schema(s: Union[Schema, Type[Schema]] = None,
           request: Union[Schema, Type[Schema]] = None,
           response: Union[Schema, Type[Schema]] = None):
    request_schema = request or s
    response_schema = response or s

    if request_schema and not isinstance(request_schema, Schema):
        request_schema = request_schema()

    if response_schema and not isinstance(response_schema, Schema):
        response_schema = response_schema()

    def decorator(fn):
        def patched(*args, **kwargs):
            try:
                if request_schema:
                    data = request_schema.load(current_request.json)
                    resp = fn(*args, data=data, **kwargs)
                else:
                    resp = fn(*args, **kwargs)
                if isinstance(resp, Response):
                    return resp
                elif resp:
                    return response_schema.dump(resp) if response_schema else resp
                else:
                    return None
            except ValidationError as error:
                resp = BadRequest()
                resp.cause = error
                resp.data = {
                    'fields': error.normalized_messages()
                }
                raise resp

        return patched

    return decorator
