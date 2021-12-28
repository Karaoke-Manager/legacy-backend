__all__ = ["Tus"]

from abc import ABC, abstractmethod
from enum import Enum
from functools import cached_property
from typing import AsyncGenerator, Generic, List, Optional, Sequence, Type, TypeVar

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Request, UploadFile
from fastapi.params import Param
from starlette.responses import Response
from starlette.status import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_410_GONE,
    HTTP_412_PRECONDITION_FAILED,
    HTTP_415_UNSUPPORTED_MEDIA_TYPE,
)

CONTENT_TYPE_HEADER = "Content-Type"
UPLOAD_OFFSET_HEADER = "Upload-Offset"
CACHE_CONTROL_HEADER = "Cache-Control"
UPLOAD_LENGTH_HEADER = "Upload-Length"
TUS_VERSION_HEADER = "Tus-Version"
TUS_RESUMABLE_HEADER = "Tus-Resumable"
TUS_EXTENSION_HEADER = "Tus-Extension"
TUS_MAX_SIZE_HEADER = "Tus-Max-Size"


class Extension(str, Enum):
    CREATION = "creation"
    CREATION_WITH_UPLOAD = "creation-with-upload"
    EXPIRATION = "expiration"
    CHECKSUM = "checksum"
    TERMINATION = "termination"
    CONCATENATION = "concatenation"


class TusError(Exception):
    pass


class TusUploadNotFoundError(Exception):
    pass


class TusPermissionDeniedError(Exception):
    pass


class TusUploadGoneError(Exception):
    pass


# TODO: Find a better way to handle Cache-Control Headers
# TODO: Customization of Parameter Docs
# TODO: Pluggable authentication??
# TODO: Implement TusFileUploadHandler for storing files in a directory.


class TusUploadHandler(ABC):
    @classmethod
    @property
    def max_upload_size(cls) -> Optional[int]:
        """Return the maximum upload size (if any) for this handler."""
        return None

    @classmethod
    @property
    def extensions(cls) -> List[Extension]:
        """A list of extensions supported by this upload handler."""
        return []

    @abstractmethod
    def __init__(self, file_id: str):
        pass

    @property
    @abstractmethod
    def current_offset(self) -> int:
        pass

    @abstractmethod
    def patch(self, stream: AsyncGenerator[bytes, None]):
        pass

    @property
    @abstractmethod
    def total_size(self) -> int:
        pass


UploadHandler = TypeVar("UploadHandler", bound=TusUploadHandler)


class Tus(Generic[UploadHandler]):
    """
    This class implements a way to add an upload server to your application that is
    compatible with the TUS upload protocol.

    TODO: Usage explanation
    """

    protocol_versions = ["1.0.0"]

    def __init__(
        self,
        handler: Type[UploadHandler],
        prefix: str = "",
    ):
        self.prefix = prefix
        self.handler = handler
        self.options_dependencies: Sequence[Depends] = []
        self.head_dependencies: Sequence[Depends] = []
        self.patch_dependencies: Sequence[Depends] = []

    def tus_version(
        self,
        request: Request,
        version: Optional[str] = Header(
            None,
            alias=TUS_RESUMABLE_HEADER,
            description="The Tus protocol version.",
            example="1.0.0",
        ),
    ):
        """
        Validates that the TUS version specified by the client is compatible with the
        server. If the versions do not match, a 412 error raised. This function is
        intended to be used as a FastAPI dependency.

        :param request: The request object.
        :param version: The version specified by the client.
        :return: The version to be used for this request.
        """
        if isinstance(version, Param):
            # This is for the cases where we call tus_version with just a request object
            version = request.headers.get(TUS_RESUMABLE_HEADER, None)
        if version not in self.protocol_versions:
            raise HTTPException(
                status_code=HTTP_412_PRECONDITION_FAILED,
                detail="Incompatible Tus protocol version.",
                headers={TUS_VERSION_HEADER: ",".join(self.protocol_versions)},
            )
        return version

    def validate_content_type(
        self,
        request: Request,
        content_type: str = Header(
            ...,
            alias=CONTENT_TYPE_HEADER,
            description="The uploaded content type. Must be "
            "`application/offset+octet-stream`.",
            example="application/offset+octet-stream",
        ),
    ) -> None:
        """
        Validates that the request content type is valid according to the TUS
        specification and raises a 415 error if it is not.

        :param request: The request object.
        :param content_type: The content type specified by the client.
        """
        version = self.tus_version(request)
        if isinstance(content_type, Param):
            content_type = request.headers.get(CONTENT_TYPE_HEADER, None)
        if content_type != "application/offset+octet-stream":
            raise HTTPException(
                status_code=HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Only the content type 'application/offset+octet-stream' is "
                "accepted.",
                headers={TUS_RESUMABLE_HEADER: version},
            )

    def get_upload(
        self,
        request: Request,
        file_id: str = Path(
            ..., alias="id", description="The ID of the resumable upload."
        ),
    ) -> UploadHandler:
        version = self.tus_version(request)
        try:
            return self.handler(file_id)
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

    def create_tus_endpoint(self, router: APIRouter, path: str) -> None:
        @router.options(
            path,
            response_class=Response,
            dependencies=self.options_dependencies,
            **self.options_schema,
        )
        async def options():
            return self._options()

    @cached_property
    def router(self) -> APIRouter:
        """
        Returns the FastAPI router that handles this resumable upload server. Note that
        this method/property is being cached. After the first invocation you should not
        make any more changes to the properties of the ``Tus`` instance as it may lead
        to inconsistent results.

        :return: A FastAPI router that can be included in your routes.
        """
        handler = self.handler
        router = APIRouter(
            prefix=self.prefix,
            default_response_class=Response,
        )

        @router.head(
            "/{id}",
            dependencies=[Depends(self.tus_version), *self.head_dependencies],
            **self.head_schema,
        )
        async def head(
            version: str = Depends(self.tus_version),
            upload: handler = Depends(self.get_upload),
        ) -> Response:
            return self._head(version, upload)

        @router.patch(
            "/{id}",
            dependencies=[
                Depends(self.validate_content_type),
                *self.patch_dependencies,
            ],
            **self.patch_schema,
        )
        async def patch(
            request: Request,
            version: str = Depends(self.tus_version),
            upload: handler = Depends(self.get_upload),
            upload_offset: int = Header(
                ...,
                description="The offset at which to append the data. Must match the "
                "current offset of the upload.",
            ),
        ) -> Response:
            return self._patch(version, upload, upload_offset, request)

        return router

    @property
    def _responses_schema(self):
        return {
            HTTP_412_PRECONDITION_FAILED: {
                "description": "The tus version requested by the client cannot be "
                "fulfilled by the server.",
            },
            HTTP_404_NOT_FOUND: {
                "description": "The resumable upload `{id}` does not exist."
            },
            HTTP_410_GONE: {
                "description": "The resumable upload `{id}` did exist, but does not"
                " anymore."
            },
            HTTP_403_FORBIDDEN: {
                "description": "Access to the resumable upload is forbidden."
            },
        }

    @property
    def options_schema(self):
        return dict(
            summary="Get TUS options",
            description="Returns an empty response with TUS headers (such as "
            "`Tus-Extensions`) that identify the parts of the protocol the server "
            "supports.",
            status_code=HTTP_204_NO_CONTENT,
            response_description="An empty response with Tus headers.",
        )

    def _options(self) -> Response:
        response = Response(
            status_code=HTTP_204_NO_CONTENT,
            headers={
                TUS_RESUMABLE_HEADER: self.protocol_versions[0],
                TUS_VERSION_HEADER: ",".join(self.protocol_versions),
            },
        )
        extensions = self.handler.extensions
        max_upload_size = self.handler.max_upload_size
        if extensions:
            response.headers[TUS_EXTENSION_HEADER] = ",".join(extensions)
        if max_upload_size:
            response.headers[TUS_MAX_SIZE_HEADER] = str(max_upload_size)
        return response

    @property
    def head_schema(self):
        return dict(
            summary="Fetches the current progress of the upload.",
            description="Query the server for the current progress of an upload. The "
            "response will contain an `Upload-Offset` header.",
            status_code=HTTP_200_OK,
            response_description="The `Upload-Offset` header identifies the number of "
            "bytes that have already been uploaded.",
            responses=self._responses_schema,
        )

    def _head(self, version: str, upload: UploadHandler):
        response = Response(
            status_code=HTTP_200_OK,
            headers={
                UPLOAD_OFFSET_HEADER: upload.current_offset,
                CACHE_CONTROL_HEADER: "no-store",
                TUS_RESUMABLE_HEADER: version,
            },
        )
        if upload.total_size is not None:
            response.headers[UPLOAD_LENGTH_HEADER] = str(upload.total_size)
        return response

    @property
    def patch_schema(self):
        return dict(
            summary="Upload a chunk of data",
            description="Append a chunk of data to the resumable upload `{id}` at the "
            "offset specified by the `Upload-Offset` header.",
            status_code=HTTP_204_NO_CONTENT,
            response_description="The data was uploaded successfully.",
            responses=self._responses_schema,
        )

    def _patch(
        self, version: str, upload: UploadHandler, upload_offset: int, request: Request
    ):
        if upload.current_offset != upload_offset:
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail="Upload Offset does not match.",
                headers={TUS_RESUMABLE_HEADER: version},
            )
        upload.patch(request.stream())
        return Response(
            status_code=HTTP_204_NO_CONTENT,
            headers={
                TUS_RESUMABLE_HEADER: version,
                UPLOAD_OFFSET_HEADER: upload.current_offset,
            },
        )
