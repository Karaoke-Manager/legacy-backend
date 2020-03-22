from marshmallow import fields, ValidationError, validates_schema, post_load

from karman.models import ModelSchema, User


class UserSchema(ModelSchema):
    __model__ = User

    class Meta:
        fields = ("id", "username")

    id = fields.Integer()
    username = fields.String()
    password = fields.String(load_only=True)

    @validates_schema
    def validate_user(self, data, **kwargs):
        if not data.get("id", None) and not data.get("username"):
            raise ValidationError("must specify either id or username")

    @post_load
    def make_user(self, data, **kwargs) -> "User":
        user = User.query.filter_by(username=data["username"]).first()
        if not user:
            raise ValidationError("user does not exist", data=data, **kwargs)
        return user
