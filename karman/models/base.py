import abc
from typing import List, Type, TypeVar, AsyncIterator, Union, TYPE_CHECKING, Any

from bson.codec_options import TypeEncoder, CodecOptions, TypeRegistry
from fastapi import routing
from funcy import monkey
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, DictIntStrAny, DictStrAny

from karman.helpers.mongo import MongoID

__all__ = ["Document", "Migration"]


class SetEncoder(TypeEncoder):
    python_type = set

    def transform_python(self, value):
        return list(value)


class FrozensetEncoder(TypeEncoder):
    python_type = frozenset

    def transform_python(self, value):
        return list(value)


encoders: List[TypeEncoder] = [SetEncoder(), FrozensetEncoder()]

DocumentType = TypeVar("DocumentType", bound='Document')


class Document(BaseModel):
    def __init_subclass__(cls: Type["Document"], **kwargs):
        super().__init_subclass__(**kwargs)

        class Encoder(TypeEncoder):
            python_type = cls

            def transform_python(self, value: cls):
                return value.document()

        # encoders.append(Encoder())

    __collection__: str
    id: MongoID = Field(None, alias="_id")

    class Config:
        validate_all = True
        validate_assignment = True
        allow_population_by_field_name = True

    def document(self, *,
                 include: Union['AbstractSetIntStr', 'DictIntStrAny'] = None,
                 exclude: Union['AbstractSetIntStr', 'DictIntStrAny'] = None) -> 'DictStrAny':
        return self.dict(by_alias=True,
                         include=include,
                         exclude=exclude,
                         exclude_defaults=True)

    @classmethod
    def collection(cls, db: AsyncIOMotorDatabase) -> AsyncIOMotorCollection:
        codec_options = CodecOptions(type_registry=TypeRegistry(encoders))
        return db.get_collection(cls.__collection__, codec_options=codec_options)

    @classmethod
    async def get(cls, db: AsyncIOMotorDatabase, document_id: Union[str, MongoID]):
        if isinstance(document_id, str):
            document_id = MongoID(document_id)
        return cls.collection(db).find_one({"_id": document_id})

    @classmethod
    async def all(cls: Type[DocumentType], db: AsyncIOMotorDatabase, **kwargs) -> AsyncIterator[DocumentType]:
        async for doc in cls.collection(db).find():
            yield cls(**doc)

    async def reload(self, db: AsyncIOMotorDatabase):
        updated = self.__class__(**await self.collection(db).find_one({"_id": self.id}))
        object.__setattr__(self, '__dict__', updated.__dict__)

    async def insert(self, db: AsyncIOMotorDatabase):
        result = await self.collection(db).insert_one(self.document())
        self.id = result.inserted_id

    @classmethod
    async def batch_create(cls, db: AsyncIOMotorDatabase, *objects: "Document"):
        await cls.collection(db).insert_many([o.document() for o in objects])


@monkey(routing)
def _prepare_response_content(res: Any, *, by_alias: bool = True, exclude_unset: bool):
    if isinstance(res, Document):
        return res
    return _prepare_response_content.original(res, by_alias=by_alias, exclude_unset=exclude_unset)


migration_names = set()


class Migration(abc.ABC):

    def __init_subclass__(cls, *args, **kwargs):
        if not hasattr(cls, "name") or not cls.name:
            raise AttributeError("Migrations must have a name")
        if cls.name in migration_names:
            raise ValueError(f'Name "{cls.name}" is already in use.')
        migration_names.add(cls.name)
        super().__init_subclass__(*args, **kwargs)

    name: str
    dependencies: List[Type["Migration"]] = []

    @classmethod
    @abc.abstractmethod
    async def execute(cls, db: AsyncIOMotorDatabase):
        raise NotImplementedError
