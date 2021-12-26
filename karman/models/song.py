import ormar

from .base import BaseMeta


class Song(ormar.Model):
    class Meta(BaseMeta):
        tablename = "songs"

    id: int = ormar.Integer(primary_key=True, description="")
