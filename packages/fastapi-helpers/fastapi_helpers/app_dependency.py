import inspect
from functools import wraps
from typing import AsyncGenerator, Generator

from starlette.applications import Starlette

__all__ = ["app_dependency"]


def app_dependency(app: Starlette, name: str = None):
    def decorator(fn):
        attr_name = "app_" + (name if name else fn.__name__)
        if inspect.isasyncgenfunction(fn):
            it: AsyncGenerator

            async def startup():
                nonlocal it
                it = fn()
                setattr(app, attr_name, await it.__anext__())

            async def shutdown():
                try:
                    await it.__anext__()
                except StopAsyncIteration:
                    pass
        elif inspect.iscoroutinefunction(fn):
            async def startup():
                setattr(app, attr_name, await fn())

            shutdown = None
        elif inspect.isgeneratorfunction(fn):
            it: Generator

            def startup():
                nonlocal it
                it = fn()
                setattr(app, attr_name, next(it))

            def shutdown():
                try:
                    next(it)
                except StopIteration:
                    pass
        elif inspect.isfunction(fn):
            def startup():
                setattr(app, attr_name, fn())

            shutdown = None
        else:
            raise ValueError("Unsupported app dependency")

        app.on_event("startup")(startup)
        if shutdown is not None:
            app.on_event("shutdown")(shutdown)

        @wraps(fn)
        async def dependency():
            return getattr(app, attr_name, None)

        return dependency

    return decorator
