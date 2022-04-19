import ormar

from .base import BaseMeta


class User(ormar.Model):
    class Meta(BaseMeta):
        tablename = "users"

    id: int = ormar.Integer(primary_key=True, description="The User ID.")
    username: str = ormar.Text(unique=True, description="The unique username.")
    password: str = ormar.Text(description="The hashed password.")
