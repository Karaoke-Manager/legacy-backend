from bson import ObjectId

from karman.models.base import Document

__all__ = ["Import"]


class Import(Document):
    name: str
    user: ObjectId
    songs: list  # TODO: List[Song]
