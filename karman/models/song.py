__all__ = ["Song"]

from .base import BaseModel


class Song(BaseModel):
    """
    This class represents a single song in the database.
    """

    __tablename__ = "songs"
