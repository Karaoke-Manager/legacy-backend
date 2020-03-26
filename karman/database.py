from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from karman.settings import settings

engine: Engine = None


def get_db_engine(**kwargs) -> Engine:
    global engine
    if engine is None:
        engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
            **kwargs
        )
    return engine


BaseSession: Session = None


def make_session() -> Session:
    global BaseSession
    if BaseSession is None:
        BaseSession = sessionmaker()
        BaseSession.configure(autocommit=False, autoflush=False, bind=get_db_engine())
    return BaseSession()


def database() -> Session:
    session = make_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
