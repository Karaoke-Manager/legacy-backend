from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# def get_or_create(cls, search=None, **kwargs):
#     if search is None:
#         search = kwargs
#     elif isinstance(search, str):
#         search = {search: kwargs[search]}
#     elif isinstance(search, list):
#         search = {key: kwargs[key] for key in search}
#     instance = db.session.query(cls).filter_by(**search).first()
#     if not instance:
#         instance = cls(**kwargs)
#         db.session.add(instance)
#     return instance
from karman.settings import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
Session = sessionmaker()
Session.configure(autocommit=False, autoflush=False, bind=engine)


async def db() -> Session:
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
