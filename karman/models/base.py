import abc
from typing import List, Type

from bson import ObjectId
from bson.codec_options import TypeEncoder, CodecOptions, TypeRegistry
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pydantic import BaseModel
from pymongo.database import Database

__all__ = ["Document", "Migration"]


def patch_oid_class():
    def get_oid_validators():
        yield validate_object_id

    def validate_object_id(value):
        return ObjectId(value)

    def modify_oid_schema(field_schema):
        # TODO: Is this right?
        field_schema.update(
            type="string",
            length=24
        )

    ObjectId.__get_validators__ = get_oid_validators
    ObjectId.__modify_schema__ = modify_oid_schema


patch_oid_class()


class SetEncoder(TypeEncoder):
    python_type = set

    def transform_python(self, value):
        return list(value)


class FrozensetEncoder(TypeEncoder):
    python_type = frozenset

    def transform_python(self, value):
        return list(value)


encoders: List[TypeEncoder] = [SetEncoder(), FrozensetEncoder()]


class Document(BaseModel):
    def __init_subclass__(cls: Type["Document"], **kwargs):
        super().__init_subclass__(**kwargs)

        class Encoder(TypeEncoder):
            python_type = cls

            def transform_python(self, value: cls):
                return value.dict()

        encoders.append(Encoder())

    __collection__: str
    _id: ObjectId = None

    class Config:
        validate_all = True
        validate_assignment = True

    @classmethod
    def collection(cls, db: AsyncIOMotorDatabase) -> AsyncIOMotorCollection:
        codec_options = CodecOptions(type_registry=TypeRegistry(encoders))
        return db.get_collection(cls.__collection__, codec_options=codec_options)

    async def insert(self, db: AsyncIOMotorDatabase):
        await self.collection(db).insert_one(self.dict())

    @classmethod
    async def batch_create(cls, db: AsyncIOMotorDatabase, *objects: "Document"):
        await cls.collection(db).insert_many([o.dict() for o in objects])


migration_names = set()


class Migration(abc.ABC):

    def __init_subclass__(cls, *args, **kwargs):
        if cls.name in migration_names:
            raise ValueError(f'Name "{cls.name}" is already in use.')
        migration_names.add(cls.name)
        super().__init_subclass__(*args, **kwargs)

    name: str
    dependencies: List[Type["Migration"]] = []

    @classmethod
    def validate(cls):
        if not hasattr(cls, "name") or not cls.name:
            raise AttributeError("Migrations must have a name")

    @classmethod
    @abc.abstractmethod
    def execute(cls, db: Database):
        raise NotImplementedError
