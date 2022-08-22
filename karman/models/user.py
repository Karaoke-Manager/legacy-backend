__all__ = ["User"]

from sqlalchemy import Column, Text

from .base import BaseModel


class User(BaseModel):
    """
    This class represents a user in the database.
    """

    __tablename__ = "users"

    username: str = Column(Text, unique=True)
    password: str = Column(Text)
