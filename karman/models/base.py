__all__ = ["BaseModel"]

from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, MetaData
from sqlalchemy.orm import as_declarative


@as_declarative()
class BaseModel:
    """
    This is the base class for all database models. It is a SQLAlchemy declarative base.
    The ``metadata`` of this class contains data about all tables used by the Karman
    API.
    """

    if TYPE_CHECKING:
        metadata: MetaData

    __mapper_args__ = {"eager_defaults": True}

    id: int = Column(Integer, primary_key=True)
