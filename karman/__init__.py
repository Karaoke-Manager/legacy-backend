from fastapi import FastAPI
from starlette.responses import RedirectResponse

from alembic_data import register_object
from karman import api
from karman.models import Scope
from karman.scopes import all_scopes
from karman.settings import settings

for scope_name in all_scopes.keys():
    register_object(Scope, name=scope_name)

app = FastAPI(title=settings.application_name,
              openapi_url=settings.openapi_path,
              debug=settings.debug)
app.include_router(api.v1, prefix="/v1")


@app.get("/", include_in_schema=False)
def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse("/docs")
