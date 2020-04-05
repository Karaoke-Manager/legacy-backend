from karman.helpers.mongo import MongoID
from motor_odm import Document

__all__ = ["Import"]


class Import(Document):
    class Meta:
        collection = "import"

    name: str
    user: MongoID
    songs: list  # TODO: List[Song]
