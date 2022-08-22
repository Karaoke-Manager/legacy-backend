__all__ = ["get_app"]

from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, FastAPI
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from karman.settings import Settings
from karman.util.versioning import select_routes, strict_version_selector

from ..exceptions import HTTPException
from ..routes import oauth, songs, users
from ..util import openapi


def get_app(
    servers: Optional[List[Dict[str, Union[str, Any]]]] = None,
) -> FastAPI:
    """
    Creates a FastAPI app instance that serves the v1 API, typically located at /v1/...
    The app can be used standalone but will typically only be mounted by the main app.

    :param servers: The servers identifying where the v1 API will be served. This is
                    used. for OpenAPI documentation and is necessary to make the
                    interactive docs work.
    """

    settings = Settings.instance()

    api = APIRouter()
    api.include_router(oauth.router)
    api.include_router(users.router, prefix="/users")
    api.include_router(songs.router, prefix="/songs")

    # FIXME: Make these configurable?
    v1 = FastAPI(
        title="Karman API",
        version="1.0",
        license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
        openapi_url="/openapi.json",
        debug=settings.debug,
        servers=servers,
    )
    select_routes(api, v1, strict_version_selector(1))
    openapi.remove_body_schemas(v1)
    openapi.remove_hidden_responses(v1)

    @v1.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exception: HTTPException
    ) -> Response:
        content = {"code": exception.error_code, "message": exception.message}
        if exception.detail:
            content["detail"] = exception.detail
        return JSONResponse(
            status_code=exception.status_code,
            content=content,
            headers=exception.headers or {},
        )

    @v1.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(
        request: Request, exception: StarletteHTTPException
    ) -> Response:
        # Catch automatically generated exceptions
        if exception.status_code == status.HTTP_404_NOT_FOUND:
            content = {
                "code": "apiNotFound",
                "message": "This API endpoint does not exist.",
            }
        elif exception.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            content = {
                "code": "methodNotAllowed",
                "message": f"This endpoint does not respond to {request.method} "
                "requests.",
            }
        else:
            content = {"code": "unknown", "message": "an unknown error occurred."}
        if exception.detail:
            content["detail"] = exception.detail

        return JSONResponse(
            status_code=exception.status_code,
            content=content,
            headers=getattr(exception, "headers", {}),
        )

    return v1
