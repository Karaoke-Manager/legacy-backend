import asyncio
from typing import Any, Callable, Coroutine, Dict, Optional, Type

from fastapi.routing import APIRoute, Request, Response
from starlette.concurrency import run_in_threadpool


class ErrorHandlingAPIRoute(APIRoute):
    exception_handlers: Dict[Type, Callable]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls.exception_handlers = {}

    @classmethod
    def exception_handler(cls, exc_class: Type[Exception]) -> Callable:
        def decorator(func: Callable) -> Callable:
            cls.add_exception_handler(exc_class, func)
            return func

        return decorator

    @classmethod
    def add_exception_handler(
        cls,
        exc_class: Type[Exception],
        handler: Callable,
    ) -> None:
        cls.exception_handlers[exc_class] = handler

    @classmethod
    def _lookup_exception_handler(
        cls, exc: Exception
    ) -> Optional[
        Callable[[Request, Exception], Response | Coroutine[Any, Any, Response]]
    ]:
        for exc_cls in type(exc).__mro__:
            if exc_cls in cls.exception_handlers:
                return cls.exception_handlers[exc_cls]
        return None

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except Exception as exc:
                handler = self._lookup_exception_handler(exc)
                if handler is None:
                    raise exc
                if asyncio.iscoroutinefunction(handler):
                    return await handler(request, exc)  # type: ignore
                else:
                    return await run_in_threadpool(
                        handler, request, exc  # type: ignore
                    )

        return custom_route_handler
