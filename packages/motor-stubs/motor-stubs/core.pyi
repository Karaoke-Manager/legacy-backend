from typing import (Any, Type, Generic, Optional, TypeVar, Union, Literal, Callable, Awaitable, Mapping, MutableMapping,
                    Tuple, Sequence, Collection, List, Iterable, AsyncIterator)

from bson import CodecOptions, Timestamp, SON, DBRef, ObjectId, Code
from bson.raw_bson import RawBSONDocument
from pymongo import (ReadPreference, WriteConcern, monitoring, InsertOne, UpdateOne, UpdateMany, ReplaceOne, DeleteOne,
                     DeleteMany, IndexModel)
from pymongo.client_session import SessionOptions, TransactionOptions, ClientSession
from pymongo.collation import Collation
from pymongo.cursor import Cursor
from pymongo.read_concern import ReadConcern
from pymongo.results import BulkWriteResult, DeleteResult, InsertManyResult, InsertOneResult, UpdateResult
from pymongo.son_manipulator import SONManipulator

Size = int
Count = int
Time = int
Address = Tuple[str, int]
CursorID = str  # TODO: what is this type

Document = Union[MutableMapping[str, Any], RawBSONDocument, SON]
UpdateDocument = Document
AggregationStage = Document
AggregationPipeline = List[AggregationStage]  # TODO: This is probably false / an implementation error

Query = Mapping[str, Any]
Direction = Literal[1, -1]  # [pymongo.ASCENDING, pymongo.DESCENDING]
IndexSpecifier = Literal['2d', 'geoHaystack', '2dsphere', 'hashed', 'text']
Index = List[Tuple[str, Union[Direction, IndexSpecifier]]]
Sort = List[Tuple[str, Direction]]
Projection = Union[List[str], Mapping[str, Any]]
ReturnDocument = Literal[True, False]  # [ReturnDocument.BEFORE, ReturnDocument.AFTER]
FullDocument = Optional[Literal["updateLookup"]]
AllowableErrors = list  # TODO: Refine this type
Output = Union[str, Document, SON]
OptionsType = Document
Limit = Tuple[str, Count]
JavaScriptFunctionType = Union[str, Code]

WriteOperation = Union[InsertOne, UpdateOne, UpdateMany, ReplaceOne, DeleteOne, DeleteMany]
ValidationResult = dict
ProfilingLevel = Literal[0, 1, 2]  # [pymongo.OFF, pymongo.SLOW_ONLY, pymongo.ALL]
ProfilingInfo = list

ClientSessionType = TypeVar("ClientSessionType", bound="AgnosticClientSession")
ClientType = TypeVar("ClientType", bound="AgnosticClient")
DatabaseType = TypeVar("DatabaseType", bound="AgnosticDatabase")
CollectionType = TypeVar("CollectionType", bound="AgnosticCollection")
CursorType = TypeVar("CursorType", bound="AgnosticCursor")
CommandCursorType = TypeVar("CommandCursorType", bound="AgnosticCommandCursor")
RawBatchCursorType = TypeVar("RawBatchCursorType", bound="AgnosticRawBatchCursor")
LatentCommandCursorType = TypeVar("LatentCommandCursorType", bound="AgnosticLatentCommandCursor")
ChangeStreamType = TypeVar("ChangeStreamType", bound="AgnosticChangeStream")


class AgnosticBase(object):
    def __init__(self, delegate: AgnosticBase) -> None: ...


class AgnosticBaseProperties(AgnosticBase):
    @property
    def codec_options(self) -> CodecOptions: ...

    @property
    def read_preference(self) -> ReadPreference: ...

    @property
    def read_concern(self) -> ReadConcern: ...

    @property
    def write_concern(self) -> WriteConcern: ...


class AgnosticClient(Generic[ClientSessionType, DatabaseType, CommandCursorType, ChangeStreamType],
                     AgnosticBaseProperties):
    HOST: str
    PORT: int

    @property
    def address(self) -> Address: ...

    @property
    def arbiters(self) -> Sequence[Address]: ...

    def close(self) -> None: ...

    async def drop_database(self, name_or_database: Union[str, DatabaseType],
                            session: ClientSessionType = ...) -> None: ...

    @property
    def event_listeners(self) -> Sequence[monitoring._EventListener]: ...

    async def fsync(self, **kwargs) -> None: ...

    def get_database(self, name: str = ...,
                     codec_options: CodecOptions = ...,
                     read_preference: ReadPreference = ...,
                     write_concern: WriteConcern = ...,
                     read_concern: ReadConcern = ...) -> DatabaseType: ...

    def get_default_database(self, default: str = ...,
                             codec_options: CodecOptions = ...,
                             read_preference: ReadPreference = ...,
                             write_concern: WriteConcern = ...,
                             read_concern: ReadConcern = ...) -> DatabaseType: ...

    @property
    def is_mongos(self) -> bool: ...

    @property
    def is_primary(self) -> bool: ...

    async def list_databases(self, session: ClientSessionType = ...) -> CommandCursorType: ...

    async def list_database_names(self) -> Sequence[str]: ...

    @property
    def local_threshold_ms(self) -> Time: ...

    @property
    def max_bson_size(self) -> Size: ...

    @property
    def max_idle_time_ms(self) -> Time: ...

    @property
    def max_message_size(self) -> Size: ...

    @property
    def max_pool_size(self) -> Size: ...

    @property
    def max_write_batch_size(self) -> Size: ...

    @property
    def min_pool_size(self) -> Size: ...

    @property
    def nodes(self) -> Sequence[Address]: ...

    @property
    def primary(self) -> Address: ...

    @property
    def retry_reads(self) -> bool: ...

    @property
    def retry_writes(self) -> bool: ...

    @property
    def secondaries(self) -> Sequence[Address]: ...

    @property
    async def server_info(self) -> Document: ...

    @property
    def server_selection_timeout(self) -> Time: ...

    async def start_session(self, causal_consistency: bool = ...,
                            default_transaction_options: TransactionOptions = ...) -> ClientSessionType: ...

    async def unlock(self, session: ClientSessionType) -> None: ...

    def __init__(self,
                 host: str = ...,
                 port: int = ...,
                 document_class: Type[Document] = ...,
                 tz_aware: bool = ...,
                 connect: bool = ...,
                 **kwargs) -> None: ...

    def watch(self, pipeline: List[dict] = ...,
              full_document: FullDocument = ...,
              resume_after: ObjectId = ...,
              max_await_time_ms: Time = ...,
              batch_size: Size = ...,
              collation: Collation = ...,
              start_at_operation_time: Timestamp = ...,
              session: ClientSessionType = ...,
              start_after: ObjectId = ...) -> ChangeStreamType: ...

    def __getattr__(self, item: str) -> DatabaseType: ...

    def __getitem__(self, name: str) -> DatabaseType: ...

    def get_io_loop(self): ...


class AgnosticClientSession(Generic[ClientType], AgnosticBase):
    T = TypeVar("T")

    def __init__(self, delegate: ClientSession, motor_client: ClientType) -> None: ...

    async def with_transaction(self: ClientSessionType, coro: Callable[[ClientSessionType], Awaitable[T]],
                               read_concern: ReadConcern = ...,
                               write_concern: WriteConcern = ...,
                               read_preference: ReadPreference = ...,
                               max_commit_time_ms: Time = ...) -> T: ...

    def start_transaction(self, read_concern: ReadConcern = ...,
                          write_concern: WriteConcern = ...,
                          read_preference: ReadPreference = ...,
                          max_commit_time_ms: Time = ...): ...

    @property
    def client(self) -> ClientType: ...

    async def __aenter__(self: ClientSessionType) -> ClientSessionType: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...

    async def commit_transaction(self) -> None: ...

    async def abort_transaction(self) -> None: ...

    async def end_session(self) -> None: ...

    @property
    def cluster_time(self) -> Mapping[str, Timestamp]: ...

    @property
    def has_ended(self) -> bool: ...

    @property
    def in_transaction(self) -> bool: ...

    @property
    def options(self) -> SessionOptions: ...

    @property
    def operation_time(self) -> Timestamp: ...

    @property
    def session_id(self) -> RawBSONDocument: ...  # TODO: Check if the return type is correct.

    def advance_cluster_time(self, cluster_time: Mapping[str, Timestamp]) -> None: ...

    def advance_operation_time(self, operation_time: Timestamp) -> None: ...


class AgnosticDatabase(Generic[ClientSessionType,
                               ClientType,
                               CollectionType,
                               CursorType,
                               CommandCursorType,
                               LatentCommandCursorType,
                               ChangeStreamType],
                       AgnosticBaseProperties):
    async def command(self, command: Union[str, Mapping[str, Any]],
                      value: Any = ...,
                      check: bool = ...,
                      allowable_errors: AllowableErrors = ...,
                      read_preference: ReadPreference = ...,
                      codec_options: CodecOptions = ...,
                      session: ClientSessionType = ...,
                      **kwargs) -> Union[Document, CursorType]: ...

    async def create_collection(self, name: str,
                                codec_options: CodecOptions = ...,
                                read_preference: ReadPreference = ...,
                                write_concern: WriteConcern = ...,
                                read_concern: ReadConcern = ...,
                                session: ClientSessionType = ...,
                                **kwargs) -> CollectionType: ...

    async def current_op(self, include_all: bool = ..., session: ClientSessionType = ...) -> Document: ...

    async def dereference(self, dbref: DBRef, session: SessionOptions = ..., **kwargs): ...

    async def drop_collection(self, name_or_collection: Union[str, CollectionType],
                              session: ClientSessionType = ...) -> None: ...

    def get_collection(self, name: str,
                       codec_options: CodecOptions = ...,
                       read_preference: ReadPreference = ...,
                       write_concern: WriteConcern = ...,
                       read_concern: ReadConcern = ...) -> CollectionType: ...

    async def list_collection_names(self, session: ClientSessionType = ...,
                                    filter: Query = ...,
                                    **kwargs) -> Sequence[str]: ...

    async def list_collections(self, session: ClientSessionType = ...,
                               filter: Query = ...,
                               **kwargs) -> CommandCursorType: ...  # TODO: Is the return type correct?

    @property
    def name(self) -> str: ...

    async def profiling_info(self, session: ClientSessionType = ...) -> ProfilingInfo: ...

    async def profiling_level(self, session: ClientSessionType = ...) -> ProfilingLevel: ...

    async def set_profiling_level(self, level: ProfilingLevel,
                                  slow_ms: Time = ...,
                                  session: ClientSessionType = ...) -> None: ...

    async def validate_collection(self, name_or_collection: Union[str, CollectionType],
                                  scandata: bool = ...,
                                  full: bool = ...,
                                  session: ClientSessionType = ...) -> ValidationResult: ...

    def with_options(self: DatabaseType,
                     codec_options: CodecOptions = ...,
                     read_preference: ReadPreference = ...,
                     write_concern: WriteConcern = ...,
                     read_concern: ReadConcern = ...) -> DatabaseType: ...

    @property
    def incoming_manipulators(self) -> Collection[SONManipulator]: ...

    @property
    def incoming_copying_manipulators(self) -> Collection[SONManipulator]: ...

    @property
    def outgoing_manipulators(self) -> Collection[SONManipulator]: ...

    @property
    def outgoing_copying_manipulators(self) -> Collection[SONManipulator]: ...

    def __init__(self, client: ClientType,
                 name: str,
                 codec_options: CodecOptions = ...,
                 read_preference: ReadPreference = ...,
                 write_concern: WriteConcern = ...,
                 read_concern: ReadConcern = ...) -> None: ...

    def aggregate(self, pipeline: AggregationPipeline,
                  session: ClientSessionType = ...,
                  **kwargs) -> LatentCommandCursorType: ...

    def watch(self, pipeline: AggregationPipeline = ...,
              full_document: FullDocument = ...,
              resume_after: ObjectId = ...,
              max_await_time_ms: Time = ...,
              batch_size: Size = ...,
              collation: Collation = ...,
              start_at_operation_time: Timestamp = ...,
              session: ClientSessionType = ...,
              start_after: ObjectId = ...) -> ChangeStreamType: ...

    @property
    def client(self) -> ClientType: ...

    def __getattr__(self, name: str) -> CollectionType: ...

    def __getitem__(self, name: str) -> CollectionType: ...


class AgnosticCollection(Generic[ClientSessionType,
                                 DatabaseType,
                                 CursorType,
                                 RawBatchCursorType,
                                 LatentCommandCursorType,
                                 ChangeStreamType],
                         AgnosticBaseProperties):
    async def bulk_write(self, requests: List[WriteOperation],
                         ordered: bool = ...,
                         bypass_document_validation: bool = ...,
                         session: ClientSessionType = ...) -> BulkWriteResult: ...

    async def count_documents(self, filter: Query,
                              session: ClientSessionType = ...,
                              **kwargs) -> Count: ...

    async def create_index(self, keys: Union[str, Index],
                           session: ClientSessionType = ...,
                           **kwargs) -> str: ...

    async def create_indexes(self, indexes: List[IndexModel],
                             session: ClientSessionType = ...,
                             **kwargs) -> Sequence[str]: ...

    async def delete_many(self, filter: Query,
                          collation: Collation = ...,
                          session: ClientSessionType = ...) -> DeleteResult: ...

    async def delete_one(self, filter: Query,
                         collation: Collation = ...,
                         session: ClientSessionType = ...) -> DeleteResult: ...

    async def distinct(self, key: str,
                       filter: Query,
                       session: ClientSessionType = ...,
                       **kwargs) -> List[str]: ...

    async def drop(self, session: ClientSessionType = ...) -> None: ...

    async def drop_index(self, index_or_name: Union[str, Index],
                         session: ClientSessionType = ...,
                         **kwargs) -> None: ...

    async def drop_indexes(self, session: ClientSessionType = ..., **kwargs) -> None: ...

    async def estimated_document_count(self, **kwargs) -> Count: ...

    async def find_one(self, filter: Query = ..., *args, **kwargs) -> Document: ...

    async def find_one_and_delete(self, filter: Query,
                                  projection: Projection = ...,
                                  sort: Sort = ...,
                                  session: ClientSessionType = ...,
                                  **kwargs) -> Document: ...

    async def find_one_and_replace(self, filter: Query,
                                   replacement: Document,
                                   projection: Projection = ...,
                                   sort: Sort = ...,
                                   return_document: ReturnDocument = ...,
                                   session: ClientSessionType = ...,
                                   **kwargs) -> Document: ...

    async def find_one_and_update(self, filter: Query,
                                  update: Union[UpdateDocument, AggregationPipeline],
                                  projection: Projection = ...,
                                  sort: Sort = ...,
                                  upsert: bool = ...,
                                  return_document: ReturnDocument = ...,
                                  array_filters: List[Query] = ...,
                                  session: ClientSessionType = ...,
                                  **kwargs) -> Document: ...

    @property
    def full_name(self) -> str: ...

    async def index_information(self, session: ClientSessionType) -> Mapping[str, Mapping[str, Any]]: ...

    async def inline_map_reduce(self, map: JavaScriptFunctionType,
                                reduce: JavaScriptFunctionType,
                                full_response: bool = ...,
                                session: ClientSessionType = ...,
                                **kwargs) -> Union[Sequence[Document], Any]: ...

    async def insert_many(self, documents: Iterable[Document],
                          ordered: bool = ...,
                          bypass_document_validation: bool = ...,
                          session: ClientSessionType = ...) -> InsertManyResult: ...

    async def insert_one(self, document: Document,
                         bypass_document_validation: bool = ...,
                         session: ClientSessionType = ...) -> InsertOneResult: ...

    async def map_reduce(self, map: JavaScriptFunctionType,
                         reduce: JavaScriptFunctionType,
                         out: Output,
                         full_response: bool = ...,
                         session: ClientSessionType = ...,
                         **kwargs) -> CollectionType: ...

    @property
    def name(self) -> str: ...

    async def options(self, session: ClientSessionType) -> OptionsType: ...

    async def reindex(self, session: ClientSessionType = ..., **kwargs) -> None: ...

    async def rename(self, new_name: str, session: ClientSessionType = ..., **kwargs) -> None: ...

    async def replace_one(self, filter: Query,
                          replacement: Document,
                          upsert: bool = ...,
                          bypass_document_validation: bool = ...,
                          collation: Collation = ...,
                          session: ClientSessionType = ...) -> UpdateResult: ...

    async def update_many(self, filter: Query,
                          update: Document,
                          upsert: bool = ...,
                          array_filters: List[Query] = ...,
                          bypass_document_validation: bool = ...,
                          collation: Collation = ...,
                          session: ClientSessionType = ...) -> UpdateResult: ...

    async def update_one(self, filter: Query,
                         update: Document,
                         upsert: bool = ...,
                         bypass_document_validation: bool = ...,
                         collation: Collation = ...,
                         session: ClientSessionType = ...) -> UpdateResult: ...

    def with_options(self: CollectionType, codec_options: CodecOptions = ...,
                     read_preference: ReadPreference = ...,
                     write_concern: WriteConcern = ...,
                     read_concern: ReadConcern = ...) -> CollectionType: ...

    def __init__(self, database: DatabaseType,
                 name: str,
                 codec_options: CodecOptions = ...,
                 read_preference: ReadPreference = ...,
                 write_concern: WriteConcern = ...,
                 read_concern: ReadConcern = ...,
                 _delegate: Collection = ...) -> None: ...

    database: DatabaseType

    def __getattr__(self: CollectionType, name: str) -> CollectionType: ...

    def __getitem__(self: CollectionType, name: str) -> CollectionType: ...

    def find(self, filter: Query = ...,
             projection: Projection = ...,
             skip: Count = ...,
             limit: Count = ...,
             no_cursor_timeout: bool = ...,
             cursor_type: int = ...,
             sort: Sort = ...,
             allow_partial_results: bool = ...,
             oplog_replay: bool = ...,
             modifiers: dict = ...,
             batch_size: Count = ...,
             manipulate: bool = ...,
             collation: Collation = ...,
             hint: Index = ...,
             max_scan: Count = ...,
             max_time_ms: Time = ...,
             max: Limit = ...,
             min: Limit = ...,
             return_key: bool = ...,
             show_record_id: bool = ...,
             snapshot: bool = ...,
             comment: str = ...,
             session: ClientSessionType = ...) -> CursorType: ...

    def find_raw_batches(self, filter: Query = ...,
                         projection: Projection = ...,
                         skip: Count = ...,
                         limit: Count = ...,
                         no_cursor_timeout: bool = ...,
                         cursor_type: int = ...,
                         sort: Sort = ...,
                         allow_partial_results: bool = ...,
                         oplog_replay: bool = ...,
                         modifiers: dict = ...,
                         batch_size: Count = ...,
                         manipulate: bool = ...,
                         collation: Collation = ...,
                         hint: Index = ...,
                         max_scan: Count = ...,
                         max_time_ms: Time = ...,
                         max: Limit = ...,
                         min: Limit = ...,
                         return_key: bool = ...,
                         show_record_id: bool = ...,
                         snapshot: bool = ...,
                         comment: str = ...,
                         session: ClientSessionType = ...) -> RawBatchCursorType: ...

    def aggregate(self, pipeline: AggregationPipeline,
                  session: ClientSessionType = ...,
                  **kwargs) -> LatentCommandCursorType: ...

    def aggregate_raw_batches(self, pipeline: AggregationPipeline, **kwargs) -> LatentCommandCursorType: ...

    def watch(self, pipeline: List[dict] = ...,
              full_document: FullDocument = ...,
              resume_after: ObjectId = ...,
              max_await_time_ms: Time = ...,
              batch_size: Size = ...,
              collation: Collation = ...,
              start_at_operation_time: Timestamp = ...,
              session: ClientSessionType = ...,
              start_after: ObjectId = ...) -> ChangeStreamType: ...

    def list_indexes(self, session: ClientSessionType = ...) -> LatentCommandCursorType: ...


class AgnosticBaseCursor(Generic[ClientSessionType,
                                 CollectionType],
                         AsyncIterator[Document],
                         AgnosticBase):
    @property
    def address(self) -> Optional[Address]: ...

    @property
    def cursor_id(self) -> CursorID: ...

    @property
    def alive(self) -> bool: ...

    @property
    def session(self) -> Optional[ClientSessionType]: ...

    def __init__(self, cursor: Cursor, collection: CollectionType) -> None: ...

    def __aiter__(self: CursorType) -> CursorType: ...

    async def __anext__(self) -> Document: ...

    async def fetch_next(self) -> None: ...

    def next_object(self) -> Document: ...

    def each(self, callback: Callable[[Document, Exception], bool]) -> None: ...

    async def to_list(self, length: int) -> List[Document]: ...

    async def close(self) -> None: ...

    def batch_size(self: CursorType, batch_size: Count) -> CursorType: ...


class AgnosticCursor(Generic[ClientSessionType, CollectionType],
                     AgnosticBaseCursor[ClientSessionType, CollectionType]):
    @property
    def address(self) -> Address: ...

    def collation(self: CursorType, collation: Collation) -> CursorType: ...

    async def distinct(self, key: str) -> Sequence[Any]: ...

    async def explain(self) -> Document: ...

    def add_option(self: CursorType, mask: int) -> CursorType: ...

    def remove_option(self: CursorType, mask: int) -> CursorType: ...

    def limit(self: CursorType, limit: Count) -> CursorType: ...

    def skip(self: CursorType, skip: Count) -> CursorType: ...

    def max_scan(self: CursorType, max_scan: Count) -> CursorType: ...

    def sort(self: CursorType, key_or_list: Union[str, Sort], direction: Direction = ...) -> CursorType: ...

    def hint(self: CursorType, hint: Index) -> CursorType: ...

    def where(self: CursorType, code: JavaScriptFunctionType) -> CursorType: ...

    def max_await_time_ms(self: CursorType, max_await_time_ms: Time) -> CursorType: ...

    def max_time_ms(self: CursorType, max_time_ms: Time) -> CursorType: ...

    def min(self: CursorType, spec: Limit) -> CursorType: ...

    def max(self: CursorType, spec: Limit) -> CursorType: ...

    def comment(self: CursorType, comment: str) -> CursorType: ...

    def rewind(self: CursorType) -> CursorType: ...

    def clone(self: CursorType) -> CursorType: ...


class AgnosticRawBatchCursor(Generic[ClientSessionType, CollectionType],
                             AgnosticCursor[ClientSessionType, CollectionType]):
    pass


class AgnosticCommandCursor(Generic[ClientSessionType, CollectionType],
                            AgnosticBaseCursor[ClientSessionType, CollectionType]):
    pass


class AgnosticRawBatchCommandCursor(Generic[ClientSessionType, CollectionType],
                                    AgnosticCommandCursor[ClientSessionType, CollectionType]):
    pass


class AgnosticLatentCommandCursor(Generic[ClientSessionType, CollectionType],
                                  AgnosticCommandCursor[ClientSessionType, CollectionType]):
    def __init__(self, collection: CollectionType, start: Callable[[...], Awaitable], *args, **kwargs) -> None: ...


class AgnosticChangeStream(Generic[ClientSessionType],
                           AgnosticBase):
    @property
    def alive(self) -> bool: ...

    @property
    def resume_token(self) -> ObjectId: ...

    def __init__(self, target,
                 pipeline: AggregationPipeline,
                 full_document: FullDocument,
                 resume_after: ObjectId,
                 max_await_time_ms: Time,
                 batch_size: Count,
                 collation: Collation,
                 start_at_operation_time: Timestamp,
                 session: ClientSessionType,
                 start_after: ObjectId) -> None: ...

    async def next(self) -> Document: ...

    async def try_next(self) -> Optional[Document]: ...

    async def close(self) -> None: ...

    def __aiter__(self): ...

    def __anext__(self): ...

    async def __aenter__(self): ...

    async def __aexit__(self, exc_type, exc_val, exc_tb): ...
