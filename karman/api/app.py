__all__ = ["get_app"]

from fastapi import FastAPI
from starlette.responses import RedirectResponse

from .. import db
from ..settings import Settings
from . import v1


def get_app() -> FastAPI:
    """
    Creates the FastAPI app instance. The app returned by this function is ready to
    serve the Karman API.
    """

    settings = Settings.instance()
    app = FastAPI(
        title=settings.app_name,
        version="0.1",
        license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
        openapi_url="/openapi.json",
        debug=settings.debug,
    )
    app.mount("/v1", v1.get_app(servers=[{"url": "/v1"}]))

    # The API root is not currently in use, so we redirect to the documentation.
    @app.get("/", include_in_schema=False)
    def redirect_to_docs() -> RedirectResponse:
        return RedirectResponse("/v1/docs")

    app.state.engine = db.get_engine()

    @app.on_event("startup")
    async def connect_db() -> None:
        # TODO: Maybe the database connection is only established with the first session
        #       We should make sure here that the connection to the DB succeeds.
        pass

    @app.on_event("shutdown")
    async def disconnect_db() -> None:
        await app.state.engine.dispose()

    return app
