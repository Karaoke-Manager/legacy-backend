from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from karman.settings import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
Session = sessionmaker()
Session.configure(autocommit=False, autoflush=False, bind=engine)


def database() -> Session:
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
