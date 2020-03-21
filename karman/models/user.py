from marshmallow import Schema, fields, post_load, ValidationError

from .database import db


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.Text(), nullable=False, unique=True)
    password_hash = db.Column(db.Text())

    class Schema(Schema):
        id = fields.Integer()
        username = fields.String(required=True)
        password = fields.String()

        class Meta:
            fields = ("id", "username")

        @post_load
        def make_user(self, data, **kwargs) -> "User":
            user = User.query.filter_by(username=data["username"]).first()
            if not user:
                raise ValidationError("user does not exist", data=data, **kwargs)
            return user
