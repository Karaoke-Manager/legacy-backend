from fastapi import FastAPI
from starlette.responses import RedirectResponse

from karman import api
from karman.settings import settings

app = FastAPI(title=settings.application_name,
              openapi_url=settings.openapi_path,
              debug=settings.debug)
app.include_router(api.v1, prefix="/v1")


@app.get("/", include_in_schema=False)
def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse("/docs")
