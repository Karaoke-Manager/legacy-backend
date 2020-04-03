from pydantic.dataclasses import dataclass

from karman.helpers.mongo import MongoID
from karman.models.base import Document

__all__ = ["Import"]


@dataclass(init=False)
class Import(Document):
    name: str
    user: MongoID
    songs: list  # TODO: List[Song]
