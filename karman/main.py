__all__ = ["app", "v1"]

from fastapi import APIRouter, FastAPI
from starlette.responses import RedirectResponse

from karman.config import settings
from karman.routes import auth, songs
from karman.util.openapi import remove_body_schemas
from karman.versioning import select_routes, strict_version_selector

api = APIRouter()
api.include_router(songs.router, prefix="/songs")
api.include_router(auth.router)

v1 = FastAPI(
    title="Karman API",
    version="1.0",
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    openapi_url="/openapi.json",
    debug=settings.debug,
)
select_routes(api, v1, strict_version_selector(1))
remove_body_schemas(v1)

app = FastAPI(
    title=settings.app_name,
    version="0.1",
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    openapi_url="/openapi.json",
    debug=settings.debug,
)
app.mount("/v1", v1)


# The API root is not currently in use so we redirect to the documentation.
@app.get("/", include_in_schema=False)
def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse("/v1/docs")
