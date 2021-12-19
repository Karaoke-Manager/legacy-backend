__all__ = ["app"]

from fastapi import APIRouter, FastAPI
from starlette.responses import RedirectResponse

from karman.config import app_config
from karman.main.versioning import select_routes, strict_version_selector
from karman.routes import songs

api = APIRouter()
api.include_router(songs.router, prefix="/songs")

v1 = FastAPI(
    title="Karman API",
    version="1.0",
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    root_path_in_servers=False,
    openapi_url="/openapi.json",
    debug=app_config.debug,
)
select_routes(api, v1, strict_version_selector(1))

app = FastAPI(
    title=app_config.name,
    version="0.1",
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    root_path_in_servers=False,
    openapi_url=None,
    debug=app_config.debug,
)
app.mount("/v1", v1)


# The API root is not currently in use so we redirect to the documentation.
@app.get("/", include_in_schema=False)
def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse("/v1/docs")
