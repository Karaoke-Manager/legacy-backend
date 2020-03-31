from starlette.responses import RedirectResponse

from . import api
from .app import app
from .app.middleware import CustomHeadersMiddleware
from .config import app_config
from .scopes import all_scopes

__all__ = ["app"]

app.include_router(api.v1, prefix="/v1")
app_config.init_app(app)


@app.get("/", include_in_schema=False)
def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse("/docs")
