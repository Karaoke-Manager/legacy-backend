# FastAPI Dependencies


# FastAPI Routing Setup


def setup_routes(self, router: APIRouter) -> None:
    self.setup_options_route("/", router)
    self.setup_head_route("/{id}", router)
    self.setup_patch_route("/{id}", router)
    if self.backend.supports_creation():
        self.setup_post_route("/", router)


@property
def __tus_version_responses(self):
    return {
        HTTP_412_PRECONDITION_FAILED: {
            "description": "The tus version requested by the client cannot be "
            "fulfilled by the server.",
        }
    }


@property
def __tus_upload_responses(self):
    return {
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
def __tus_post_responses(self):
    return {
        HTTP_400_BAD_REQUEST: {"description": "The request is malformed."},
        HTTP_413_REQUEST_ENTITY_TOO_LARGE: {},
    }


def setup_options_route(
    self,
    path: str,
    router: APIRouter,
    *,
    status_code: Optional[int] = HTTP_204_NO_CONTENT,
    tags: Optional[List[str]] = None,
    dependencies: Optional[Sequence[Depends]] = None,
    summary: Optional[str] = "Get TUS options",
    description: Optional[str] = "Returns an empty response with TUS headers (such "
    "as `Tus-Extensions`) that identify the parts of the protocol the server "
    "supports.",
    response_description: str = "An empty response with Tus headers.",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    response_class: Type[Response] = Response,
    **kwargs,
) -> None:
    @router.options(
        path,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        response_model=Response,
        response_class=response_class,
        **kwargs,
    )
    async def options():
        return await self.options()


def setup_head_route(
    self,
    path: str,
    router: APIRouter,
    *,
    status_code: Optional[int] = HTTP_204_NO_CONTENT,
    tags: Optional[List[str]] = None,
    dependencies: Optional[Sequence[Depends]] = None,
    summary: Optional[str] = "Fetches the current progress of the upload.",
    description: Optional[str] = "Query the server for the current progress of an "
    "upload. The response will contain an `Upload-Offset` header.",
    response_description: str = "The `Upload-Offset` header identifies the "
    "number of bytes that have already been uploaded.",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    response_class: Type[Response] = Response,
    **kwargs,
) -> None:
    @router.head(
        path,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=self.__tus_version_responses
        | self.__tus_upload_responses
        | (responses or {}),
        response_model=Response,
        response_class=response_class,
        **kwargs,
    )
    async def head(
        version: str = Depends(self.version_dependency),
        upload: TusUpload = Depends(self.upload_dependency),
    ) -> Response:
        return await self.head(version, upload)


def setup_patch_route(
    self,
    path: str,
    router: APIRouter,
    *,
    status_code: Optional[int] = HTTP_204_NO_CONTENT,
    tags: Optional[List[str]] = None,
    dependencies: Optional[Sequence[Depends]] = None,
    summary: Optional[str] = "Upload a chunk of data.",
    description: Optional[str] = "Append a chunk of data to the resumable upload "
    "`{id}` at the offset specified by the `Upload-Offset` header.",
    response_description: str = "The data was uploaded successfully.",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    response_class: Type[Response] = Response,
    **kwargs,
):
    @router.patch(
        path,
        status_code=status_code,
        tags=tags,
        dependencies=[
            Depends(self.content_type_dependency),
            *dependencies,
        ],
        summary=summary,
        description=description,
        response_description=response_description,
        responses=self.__tus_version_responses
        | self.__tus_upload_responses
        | (responses or {}),
        response_model=Response,
        response_class=response_class,
        **kwargs,
    )
    async def patch(
        request: Request,
        version: str = Depends(self.version_dependency),
        upload: TusUpload = Depends(self.upload_dependency),
        upload_offset: int = Header(
            ...,
            description="The offset (in bytes) at which to append the data."
            " Must match the current offset of the upload.",
            example=69,
        ),
    ) -> Response:
        return await self.patch(version, upload, upload_offset, request)


def setup_post_route(
    self,
    path: str,
    router: APIRouter,
    *,
    status_code: Optional[int] = HTTP_201_CREATED,
    tags: Optional[List[str]] = None,
    dependencies: Optional[Sequence[Depends]] = None,
    summary: Optional[str] = "Creates a new upload.",
    description: Optional[str] = "Create a new upload. If supported the upload may "
    "contain the first chunk of data.",
    response_description: str = "The upload was created successfully.",
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
    response_class: Type[Response] = Response,
    **kwargs,
):
    @router.post(
        path,
        status_code=status_code,
        tags=tags,
        dependencies=[
            Depends(self.content_type_dependency),
            *dependencies,
        ],
        summary=summary,
        description=description,
        response_description=response_description,
        responses=self.__tus_version_responses
        | self.__tus_upload_responses
        | (responses or {}),
        response_model=Response,
        response_class=response_class,
        **kwargs,
    )
    async def post(
        request: Request,
        version: str = Depends(self.version_dependency),
        upload_length: Optional[int] = Header(
            None, description="The full size of the complete upload."
        ),
        upload_defer_length: Optional[str] = Header(
            None,
            description="Indicates that the length of the entire upload will be "
            "amended in a subsequent PATCH request.",
            example=1,
        ),
        upload_metadata: Optional[str] = Header(
            None, description="Optional metadata associated with the upload."
        ),
    ):
        return await self.post(
            version, upload_length, upload_defer_length, upload_metadata, request
        )
