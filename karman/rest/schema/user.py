from marshmallow import fields, Schema, ValidationError
from marshmallow.validate import Validator

from karman import User


class Permission(Validator):
    def __call__(self, value):
        if not User.is_perm(value):
            raise ValidationError("{} is not a valid perm".format(value))


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String()
    password = fields.String(load_only=True)
    is_admin = fields.Boolean(data_key="admin")

    user_perms = fields.List(fields.String(validate=Permission()), data_key="userPerms")
    all_perms = fields.List(fields.String(), data_key="allPerms")

    # roles = fields.List(fields.Nested(RoleSchema))
