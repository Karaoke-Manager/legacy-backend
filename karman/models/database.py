from flask_sqlalchemy import SQLAlchemy
from marshmallow import post_load
from marshmallow.schema import Schema

db = SQLAlchemy()


def get_or_create(model, search=None, **kwargs):
    if search is None:
        search = kwargs
    elif isinstance(search, str):
        search = {search: kwargs[search]}
    elif isinstance(search, list):
        search = {key: kwargs[key] for key in search}
    instance = db.session.query(model).filter_by(**search).first()
    if not instance:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
    return instance


class ModelSchema(Schema):
    __model__ = None

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)
