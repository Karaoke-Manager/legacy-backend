from marshmallow import Schema, fields

from karman.models import db


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)

    class Schema(Schema):
        id = fields.Integer(required=True)
        title = fields.String(required=True)
