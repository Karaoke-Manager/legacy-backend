from fastapi import FastAPI

from karman.config import app_config

__all__ = ["app"]

app = FastAPI(title=app_config.application_name,
              openapi_url=app_config.openapi_path,
              debug=app_config.debug)
