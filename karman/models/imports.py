from bson import ObjectId

from motor_odm import Document

__all__ = ["Import"]


class Import(Document):
    class Mongo:
        collection = "import"

    name: str
    user: ObjectId
    songs: list  # TODO: List[Song]
