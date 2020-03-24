"""Alembic-Data is an extension for alembic that creates automatic data migrations.

Data migrations (in contrast to schema migrations) are performed on the contents of database tables. They allow you to
create, update, and delete rows inside the database. Alembic-Data provides a framework to generate these migrations
automatically.

Using Alembic-Data is very simple. You can use the `register_object` function to register an object in the database.
Alembic data will make sure that the next migration creates the registered object. This is normally only useful for
tables that do not contain any user data (as the migrations would have to be generated depending on the actual data).
Instead the typical usecase is to combine the `register_object` function with the `@managed_model` decorator to tell
Alembic-Data that a model will be managed exclusively programmatically.

The `@managed_model` decorator is used on your declarative model classes. For any `@managed_model` Alembic-Data will
created your `register_object` and will additionally delete any rows from that database that do not belong to any
registered object.
"""

from typing import List, Any, Dict

from alembic.autogenerate import comparators
from alembic.autogenerate.api import AutogenContext
from alembic.operations.ops import UpgradeOps
from sqlalchemy.ext.declarative import DeclarativeMeta

from .ops import *

__all__ = ["managed_model", "register_object"]


def managed_model(cls: DeclarativeMeta) -> DeclarativeMeta:
    """Marks this model as a managed model.

    Class decorator to be used on declarative SQLAlchemy models. Using this decorator causes alembic-data to assume that
    objects for this model will only be created through code and the `register_object` function.

    :param cls: The class to be decorated. Must be a SQLAlchemy declarative class.
    :return: The decorated class, unchanged.
    """
    cls.metadata.info.setdefault("managed models", set()).add(cls)  # type: ignore
    return cls


def register_object(cls: DeclarativeMeta, **kwargs) -> None:
    """
    Registers an object to be created during a database migration.

    :param cls: The class of the declarative model class. This is used to determine which table to operate on.
    :param kwargs: Arguments used to create the object. This must uniquely identify the object as it is also used to
                  determine whether the object already exists.
    """
    cls.metadata.info.setdefault("objects", dict()).setdefault(cls, list()).append(kwargs)  # type: ignore


@comparators.dispatch_for("schema")
def compare_objects(autogen_context: AutogenContext, upgrade_ops: UpgradeOps, schemas: List[str]) -> None:
    """
    Generates appropriate data migrations for the `autogen_context` and adds them to `upgrade_ops`.
    """
    managed_models = autogen_context.metadata.info.get('managed models', set())
    objects: Dict[DeclarativeMeta, Any] = autogen_context.metadata.info.get('objects', dict())
    remaining_objects = {cls: set(cls.query.all())  # type: ignore
                         for cls in objects.keys()
                         if cls in managed_models
                         and autogen_context.dialect.has_table(autogen_context.connection.engine,
                                                               cls.__table__.name)}  # type: ignore

    # Add new objects
    for cls, datas in objects.items():
        for data in datas:
            existing_object = (cls.query.filter_by(**data).first()  # type: ignore
                               if autogen_context.dialect.has_table(autogen_context.connection.engine,
                                                                    cls.__table__.name)  # type: ignore
                               else None)
            if existing_object:
                remaining_objects.get(cls, set()).discard(existing_object)
            else:
                print("Adding " + cls.__name__ + ": " + str(data))
                upgrade_ops.ops.append(InsertRowOp(cls.__table__.name, **data))  # type: ignore

    # Remove old objects
    for cls, object_set in remaining_objects.items():
        for o in object_set:
            values = {key: getattr(o, key) for key in o.__mapper__.column_attrs.keys()}
            print("Deleting " + cls.__name__ + ": " + str(values))
            upgrade_ops.ops.append(DeleteRowOp(cls.__table__.name, **values))  # type: ignore
