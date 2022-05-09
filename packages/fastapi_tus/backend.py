from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import AsyncGenerator, Dict, Generic, Optional, Set, TypeVar


class TusExtension(str, Enum):
    CREATION = "creation"
    CREATION_WITH_UPLOAD = "creation-with-upload"
    CREATION_DEFER_LENGTH = "creation-defer-length"
    EXPIRATION = "expiration"
    CHECKSUM = "checksum"
    CHECKSUM_TRAILER = "checksum-trailer"
    TERMINATION = "termination"
    CONCATENATION = "concatenation"


class TusUpload(ABC):
    def __init__(self, upload_id: Optional[str] = None):
        self.id = upload_id
        self.size: Optional[int] = None
        self.offset: Optional[int] = None
        self.metadata: dict = {}
        self.expiration: Optional[datetime] = None

    @abstractmethod
    async def lock(self):
        pass

    @abstractmethod
    async def unlock(self):
        pass

    @abstractmethod
    async def append(self, stream: AsyncGenerator[bytes, None]):
        pass

    async def __aenter__(self):
        await self.lock()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # From now on these values should not be seen as reliable
        self.offset = None
        self.size = None
        await self.unlock()


Upload = TypeVar("Upload", bound=TusUpload)


class TusBackend(ABC, Generic[Upload]):
    @property
    def max_upload_size(self) -> Optional[int]:
        return None

    @property
    @abstractmethod
    def extensions(self) -> Set[TusExtension]:
        pass

    async def create_upload(
        self,
        metadata: Dict[str, Optional[str]],
        data: AsyncGenerator[bytes, None] = None,
    ) -> Upload:
        raise NotImplementedError

    @abstractmethod
    async def get_upload(self, upload_id: str) -> Upload:
        pass
