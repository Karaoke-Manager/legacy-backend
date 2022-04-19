__all__ = ["app", "v1"]

from fastapi import APIRouter, FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.status import HTTP_405_METHOD_NOT_ALLOWED

from karman.config import settings
from karman.exceptions import HTTPException
from karman.routes import oauth, songs, users
from karman.util.openapi import remove_body_schemas, remove_hidden_responses
from karman.versioning import select_routes, strict_version_selector

api = APIRouter()
api.include_router(oauth.router)
api.include_router(users.router, prefix="/users")
api.include_router(songs.router, prefix="/songs")

v1 = FastAPI(
    title="Karman API",
    version="1.0",
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    openapi_url="/openapi.json",
    debug=settings.debug,
)
select_routes(api, v1, strict_version_selector(1))
remove_body_schemas(v1)
remove_hidden_responses(v1)

app = FastAPI(
    title=settings.app_name,
    version="0.1",
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    openapi_url="/openapi.json",
    debug=settings.debug,
)
app.mount("/v1", v1)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exception: HTTPException):
    content = {"code": exception.error_code, "message": exception.message}
    if exception.detail:
        content["detail"] = exception.detail
    return JSONResponse(
        status_code=exception.status_code,
        content=content,
    )


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(
    request: Request, exception: StarletteHTTPException
):
    content = {"code": "unknown", "message": "an unknown error occurred."}
    if exception.detail:
        content["detail"] = exception.detail
    return JSONResponse(status_code=exception.status_code, content=content)


# The API root is not currently in use so we redirect to the documentation.
@app.get("/", include_in_schema=False)
def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse("/v1/docs")
