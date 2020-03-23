from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def get_or_create(cls, search=None, **kwargs):
    if search is None:
        search = kwargs
    elif isinstance(search, str):
        search = {search: kwargs[search]}
    elif isinstance(search, list):
        search = {key: kwargs[key] for key in search}
    instance = db.session.query(cls).filter_by(**search).first()
    if not instance:
        instance = cls(**kwargs)
        db.session.add(instance)
    return instance


db.Model.get_or_create = classmethod(get_or_create)
