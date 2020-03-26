from sqlalchemy.ext.declarative import declarative_base

from karman.database import engine

Model = declarative_base(engine)
