from marshmallow import fields, Schema


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String()
    password = fields.String(load_only=True)
    is_admin = fields.Boolean()

    user_perms = fields.List(fields.String())
    all_perms = fields.List(fields.String())

    # roles = fields.List(fields.Nested(RoleSchema))
