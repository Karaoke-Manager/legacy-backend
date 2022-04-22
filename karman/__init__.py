from functools import lru_cache
from typing import Any

from fastapi import FastAPI

from .api import get_app

app: FastAPI


@lru_cache
def __app() -> FastAPI:
    """
    Initializes the main app instance. This function will be called when the ``app``
    module attribute is being accessed.

    If you want to use the app instance programmatically it is recommended that you use
    ``karman.api.get_app`` directly.
    """
    return get_app()


def __getattr__(name: str) -> Any:
    if name == "app":
        return __app()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
