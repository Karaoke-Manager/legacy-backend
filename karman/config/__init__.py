import os
from typing import Union, List

import yaml
from fastapi import FastAPI
from funcy import cached_property
from pydantic import RedisDsn, BaseModel, PyObject, AnyUrl

from .config import StorageConfig, JWTConfig, TestConfig
from ..helpers.listify import listify


class AppConfig(BaseModel):
    class Config:
        keep_untouched = (cached_property,)

    application_name: str = "Karman"
    openapi_path: str = "/openapi.json"

    debug: bool = False

    redis: RedisDsn
    mongodb: AnyUrl

    test: TestConfig = TestConfig()
    jwt: JWTConfig
    storage: StorageConfig
    uploads: List[Union[dict, str]]

    middleware: List[Union[str, dict]]

    def init_app(self, app: FastAPI):
        for spec in self.middleware:
            if isinstance(spec, str):
                spec = {"class": spec}
            else:
                spec = dict(spec)
            middleware = PyObject.validate(spec.pop("class"))
            app.add_middleware(middleware, **spec)

        for server in self.upload_servers:
            server.register_routes(app)

        @app.on_event("shutdown")
        def close_fs():
            self.storage.filesystem.close()

    @cached_property
    @listify
    def upload_servers(self):
        for spec in self.uploads:
            if isinstance(spec, str):
                spec = {"type": spec}
            spec = dict(spec)
            server_class = PyObject.validate(spec.pop("type"))
            yield server_class(**spec)


file = os.getenv("KARMAN_CONFIG", "config.yml")
with open(file) as stream:
    app_config = AppConfig(**yaml.safe_load(stream))
