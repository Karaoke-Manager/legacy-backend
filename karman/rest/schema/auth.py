from marshmallow import Schema, fields, post_load

from karman.models import User


class AuthSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

    @post_load
    def make_user(self, data, **kwargs):
        user = User.query.filter_by(username=data["username"]).first()
        if user:
            return user, data["password"]
        else:
            return user, None
