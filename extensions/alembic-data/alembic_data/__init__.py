from alembic.autogenerate import comparators
from alembic.autogenerate.api import AutogenContext
from alembic.operations.ops import UpgradeOps
from sqlalchemy.ext.declarative import DeclarativeMeta

from .ops import *


def managed_model(cls: DeclarativeMeta):
    cls.metadata.info.setdefault("managed models", set()).add(cls)
    return cls


def register_object(cls: DeclarativeMeta, **kwargs):
    cls.metadata.info.setdefault("objects", dict()).setdefault(cls, list()).append(kwargs)


@comparators.dispatch_for("schema")
def compare_objects(autogen_context: AutogenContext,
                    upgrade_ops: UpgradeOps,
                    schemas: [str]):
    managed_models = autogen_context.metadata.info.get('managed models', set())
    objects: dict = autogen_context.metadata.info.get('objects', dict())
    remaining_objects = {cls: set(cls.query.all())
                         for cls in objects.keys()
                         if cls in managed_models
                         and autogen_context.dialect.has_table(autogen_context.connection.engine,
                                                               cls.__table__.name)}

    # Add new objects
    cls: DeclarativeMeta
    for cls, datas in objects.items():
        for data in datas:
            existing_object = cls.query.filter_by(**data).first() \
                if autogen_context.dialect.has_table(autogen_context.connection.engine, cls.__tablename__) \
                else None
            if existing_object:
                remaining_objects.get(cls, set()).discard(existing_object)
            else:
                print("Adding " + cls.__name__ + ": " + str(data))
                upgrade_ops.ops.append(AddObjectOp(cls.__table__.name, **data))

    # Remove old objects
    cls: DeclarativeMeta
    for cls, objects in remaining_objects.items():
        for o in objects:
            values = {key: getattr(o, key) for key in o.__mapper__.column_attrs.keys()}
            print("Deleting " + cls.__name__ + ": " + str(values))
            upgrade_ops.ops.append(DeleteObjectOp(o.__table__.name, **values))
