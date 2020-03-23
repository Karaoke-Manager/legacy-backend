from alembic.autogenerate import comparators
from alembic.autogenerate.api import AutogenContext
from alembic.operations.ops import UpgradeOps
from flask_sqlalchemy import DefaultMeta

from .ops import *  # noqa: F401, F403


def managed_model(cls: DefaultMeta):
    cls.metadata.info.setdefault("managed models", set()).add(cls)
    return cls


def register_object(cls: DefaultMeta, **kwargs):
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
                                                               cls.__tablename__)}

    # Add new objects
    cls: DefaultMeta
    for cls, datas in objects.items():
        for data in datas:
            existing_object = cls.query.filter_by(**data).first() \
                if autogen_context.dialect.has_table(autogen_context.connection.engine, cls.__tablename__) \
                else None
            if existing_object:
                remaining_objects.get(cls, set()).discard(existing_object)
            else:
                print("Adding " + cls.__name__ + ": " + str(data))
                upgrade_ops.ops.append(AddObjectOp(cls.__tablename__, **data))

    # Remove old objects
    cls: DefaultMeta
    for cls, objects in remaining_objects.items():
        for o in objects:
            values = {key: getattr(o, key) for key in o.__mapper__.column_attrs.keys()}
            print("Deleting " + cls.__name__ + ": " + str(values))
            upgrade_ops.ops.append(DeleteObjectOp(o.__tablename__, **values))
