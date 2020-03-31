from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from karman.models.base import Model

__all__ = ["Import"]


class Import(Model):
    __tablename__ = "import"

    id = Column(Integer(), primary_key=True)
    name = Column(String())
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="imports")
#   tags or something
