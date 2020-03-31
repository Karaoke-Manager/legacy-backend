from funcy import LazyObject
from sqlalchemy import orm
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from karman.config import app_config


@LazyObject
def db_engine() -> Engine:
    return create_engine(app_config.database, connect_args={"check_same_thread": False})


class LazySession(object):
    def __init__(self):
        self.session_maker = None

    def __call__(self, *args, **kwargs) -> orm.Session:
        if not self.session_maker:
            self.session_maker = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
        return self.session_maker()


Session = LazySession()


def database() -> orm.Session:
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
