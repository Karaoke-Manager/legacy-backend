# TODO: __all__
from enum import Enum
from functools import cached_property
from typing import AsyncGenerator, List, Optional, Sequence, Tuple
from wsgiref.handlers import format_date_time

from fastapi import HTTPException, Request
from starlette.responses import Response
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_410_GONE,
    HTTP_412_PRECONDITION_FAILED,
    HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    HTTP_415_UNSUPPORTED_MEDIA_TYPE,
)

from .backend import TusBackend, TusExtension, TusUpload
from .errors import TusPermissionDeniedError, TusUploadGoneError, TusUploadNotFoundError

TUS_VERSION_HEADER = "Tus-Version"
TUS_RESUMABLE_HEADER = "Tus-Resumable"
TUS_EXTENSION_HEADER = "Tus-Extension"
TUS_MAX_SIZE_HEADER = "Tus-Max-Size"
CONTENT_LENGTH_HEADER = "Content-Length"
CONTENT_TYPE_HEADER = "Content-Type"
UPLOAD_OFFSET_HEADER = "Upload-Offset"
CACHE_CONTROL_HEADER = "Cache-Control"
UPLOAD_LENGTH_HEADER = "Upload-Length"
UPLOAD_DEFER_LENGTH_HEADER = "Upload-Defer-Length"
UPLOAD_METADATA_HEADER = "Upload-Metadata"
UPLOAD_EXPIRES_HEADER = "Upload-Expires"


class TusServer:

    # TUS Protocol Configuration

    def __init__(self, backend: TusBackend):
        self.backend = backend
        self.allow_unversioned_requests = False

    @property
    def protocol_versions(self) -> List[str]:
        return ["1.0.0"]

    # Helper Methods

    def ensure_version(self, request: Request):
        version = request.headers.get(TUS_RESUMABLE_HEADER)
        if version is None and not self.allow_unversioned_requests:
            raise HTTPException(
                status_code=HTTP_412_PRECONDITION_FAILED,
                detail=f"Header {TUS_RESUMABLE_HEADER} is required but not present.",
                headers={
                    TUS_RESUMABLE_HEADER: self.protocol_versions[0],
                    TUS_VERSION_HEADER: ",".join(self.protocol_versions),
                },
            )
        if version is not None and version not in self.protocol_versions:
            raise HTTPException(
                status_code=HTTP_412_PRECONDITION_FAILED,
                detail="Incompatible Tus protocol version.",
                headers={
                    TUS_RESUMABLE_HEADER: self.protocol_versions[0],
                    TUS_VERSION_HEADER: ",".join(self.protocol_versions),
                },
            )
        return version

    async def get_upload(
        self, upload_id: str, request: Request, *, version: str
    ) -> TusUpload:
        try:
            return await self.backend.get_upload(upload_id)
        except TusUploadNotFoundError as error:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=next(iter(error.args), None),
                headers={TUS_RESUMABLE_HEADER: version},
            )
        except TusUploadGoneError as error:
            raise HTTPException(
                status_code=HTTP_410_GONE,
                detail=next(iter(error.args), None),
                headers={TUS_RESUMABLE_HEADER: version},
            )
        except TusPermissionDeniedError as error:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail=next(iter(error.args), None),
                headers={TUS_RESUMABLE_HEADER: version},
            )

    def encode_metadata(self, metadata: dict) -> str:
        pass

    def decode_metadata(self, metadata: str) -> dict:
        pass

    async def peek_stream(
        self, stream: AsyncGenerator[bytes, None]
    ) -> Tuple[bool, Optional[AsyncGenerator[bytes, None]]]:
        chunk: Optional[bytes] = None
        async for chunk in stream:
            if chunk:
                break
        if chunk:

            async def generator(first):
                yield first
                async for c in stream:
                    yield c

            return True, generator(chunk)
        else:
            return False, None

    # FastAPI Endpoints

    async def options(self, request: Request) -> Response:
        response = Response(
            status_code=HTTP_204_NO_CONTENT,
            headers={
                TUS_RESUMABLE_HEADER: self.protocol_versions[0],
                TUS_VERSION_HEADER: ",".join(self.protocol_versions),
            },
        )
        max_upload_size = self.backend.max_upload_size
        if self.backend.extensions:
            response.headers[TUS_EXTENSION_HEADER] = ",".join(self.backend.extensions)
        if max_upload_size:
            response.headers[TUS_MAX_SIZE_HEADER] = str(max_upload_size)
        return response

    async def head(self, upload_id: str, request: Request):
        version = self.get_version(request)
        async with self.get_upload(upload_id, request) as upload:
            response = Response(
                status_code=HTTP_204_NO_CONTENT,
                headers={
                    UPLOAD_OFFSET_HEADER: upload.offset,
                    CACHE_CONTROL_HEADER: "no-store",
                    TUS_RESUMABLE_HEADER: version,
                },
            )
            if upload.size is not None:
                response.headers[UPLOAD_LENGTH_HEADER] = str(upload.size)
            if upload.expiration:
                response.headers[UPLOAD_EXPIRES_HEADER] = format_date_time(
                    upload.expiration.timestamp()
                )
            if upload.metadata:
                response.headers[UPLOAD_METADATA_HEADER] = self.encode_metadata(
                    upload.metadata
                )
        return response

    async def patch(self, upload_id: str, request: Request):
        version = self.get_version(request)
        content_type = request.headers.get(CONTENT_TYPE_HEADER)
        if content_type != "application/offset+octet-stream":
            raise HTTPException(
                status_code=HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Content type must be application/offset+octet-stream.",
                headers={TUS_RESUMABLE_HEADER: version},
            )
        upload = await self.get_upload(upload_id, request)
        try:
            upload_offset = request.headers.get(UPLOAD_OFFSET_HEADER)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"{UPLOAD_LENGTH_HEADER} must be an integer.",
                headers={TUS_RESUMABLE_HEADER: version},
            )
        if upload_offset is None:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Header Upload-Offset required but not found.",
                headers={TUS_RESUMABLE_HEADER: version},
            )
        async with upload:
            if upload.offset != upload_offset:
                raise HTTPException(
                    status_code=HTTP_409_CONFLICT,
                    detail="Upload Offset does not match.",
                    headers={TUS_RESUMABLE_HEADER: version},
                )
            await upload.append(request.stream())
            response = Response(
                status_code=HTTP_204_NO_CONTENT,
                headers={
                    TUS_RESUMABLE_HEADER: version,
                    UPLOAD_OFFSET_HEADER: str(upload.offset),
                },
            )
            if upload.expiration:
                response.headers[UPLOAD_EXPIRES_HEADER] = format_date_time(
                    upload.expiration.timestamp()
                )
        return response

    async def post(
        self,
        url_format: Optional[str],
        request: Request,
    ) -> Response:
        version = self.get_version(request)
        upload_length = request.headers.get(UPLOAD_LENGTH_HEADER)
        upload_defer_length = request.headers.get(UPLOAD_DEFER_LENGTH_HEADER)
        upload_metadata = request.headers.get(UPLOAD_METADATA_HEADER)

        # Check Deferred Upload Length
        if upload_defer_length is not None and upload_defer_length != "1":
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Upload-Defer-Length only supports the value 1.",
                headers={TUS_RESUMABLE_HEADER: version},
            )

        # Check Upload-Length
        if upload_length is None and not upload_defer_length:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Header {UPLOAD_LENGTH_HEADER} required but not present.",
                headers={TUS_RESUMABLE_HEADER: version},
            )
        try:
            upload_length = int(upload_length)
        except ValueError:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"{UPLOAD_LENGTH_HEADER} must be an integer",
            )
        if upload_length and upload_length > self.backend.max_upload_size:
            raise HTTPException(
                status_code=HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"The upload is too large.",
                headers={
                    TUS_RESUMABLE_HEADER: version,
                    TUS_MAX_SIZE_HEADER: self.backend.max_upload_size,
                },
            )
        metadata = self.decode_metadata(upload_metadata) if upload_metadata else {}

        has_content, stream = await self.peek_stream(request.stream())
        if has_content and TusExtension.CREATION_WITH_UPLOAD in self.backend.extensions:
            self.validate_content_type(request)
        upload = await self.backend.create_upload(metadata, stream)
        response = Response(
            status_code=HTTP_201_CREATED,
            headers={
                TUS_RESUMABLE_HEADER: version,
                UPLOAD_OFFSET_HEADER: str(upload.offset),
            },
        )
        if upload.expiration:
            response.headers[UPLOAD_EXPIRES_HEADER] = format_date_time(
                upload.expiration.timestamp()
            )
        if url_format:
            response.headers["Location"] = url_format.format(id=upload.id)
        return response
