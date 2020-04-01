import inspect
from functools import wraps
from typing import AsyncGenerator, Generator, Any, Union

__all__ = ["app_dependency"]

from fastapi import FastAPI, APIRouter


def app_dependency(app: Union[FastAPI, APIRouter]):
    instance: Any = None

    def decorator(fn):
        if inspect.isasyncgenfunction(fn):
            generator: AsyncGenerator

            async def startup():
                nonlocal generator, instance
                generator = fn()
                instance = await generator.__anext__()

            async def shutdown():
                try:
                    await generator.__anext__()
                except StopAsyncIteration:
                    pass
        elif inspect.iscoroutinefunction(fn):
            async def startup():
                nonlocal instance
                instance = await fn()

            shutdown = None
        elif inspect.isgeneratorfunction(fn):
            generator: Generator

            def startup():
                nonlocal generator, instance
                generator = fn()
                instance = next(generator)

            def shutdown():
                try:
                    next(generator)
                except StopIteration:
                    pass
        elif inspect.isfunction(fn):

            def startup():
                nonlocal instance
                instance = fn()

            shutdown = None
        else:
            raise ValueError("Unsupported app dependency")

        app.router.on_startup.append(startup)
        if shutdown is not None:
            app.router.on_shutdown.insert(0, shutdown)

        @wraps(fn)
        async def dependency():
            nonlocal instance
            return instance

        return dependency

    return decorator
