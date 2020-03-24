from marshmallow import fields, post_load, Schema

from karman.models import User


class AuthSchema(Schema):
    username = fields.String(required=True, load_only=True)
    password = fields.String(required=True, load_only=True)
    access_token = fields.String(data_key="accessToken", dump_only=True)

    @post_load
    def make_user(self, data, **kwargs):
        user = User.query.filter_by(username=data["username"]).first()
        return {
            "user": user,
            "password": data["password"]
        }
