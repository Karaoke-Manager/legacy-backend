import asyncio
import inspect
from typing import Any, Callable, Coroutine, Dict, Optional, Type

from fastapi.routing import APIRoute, Request, Response
from starlette.concurrency import run_in_threadpool


def exception_handler(exc_class: Type[Exception]) -> Callable[[Callable], Callable]:
    """
    This decorator is intended to be used on static methods in subclasses of
    ``ErrorHandlingAPIRoute``. Using this decorator you can mark certain methods as
    exception handlers for specific exception. This is a more elegant alternative to
    calling ``ErrorHandlingAPIRoute#add_exception_handler`` manually.
    :param exc_class: The type of exception handled by this function.
    """

    def decorator(func: Callable) -> Callable:
        setattr(func, "_exc_class", exc_class)
        return func

    return decorator


class ErrorHandlingAPIRoute(APIRoute):
    """
    A custom subclass of `´APIRoute`` that makes it easy to handle custom exceptions.

    This might be useful over a global exception handler on the FastAPI app if you want
    to handle exceptions differently for certain routes.
    """

    exception_handlers: Dict[Type, Callable]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Initializes a new subclass. This function is responsible for implementing the
        ``@exception_handler`` decorator.
        """
        super().__init_subclass__(**kwargs)
        cls.exception_handlers = {}
        members = inspect.getmembers(cls, inspect.isfunction)
        for name, func in members:
            if hasattr(func, "_exc_class"):
                cls.add_exception_handler(func._exc_class, func)

    @classmethod
    def exception_handler(cls, exc_class: Type[Exception]) -> Callable:
        """
        This decorator is an alternative to the ``@exception_handler`` decorator on the
        module level.

        It behaves pretty much the same but allows functions outside the
        class definition to be marked as exception handler for the route.
        :param exc_class: The type of exception to be handled.
        """

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
        """
        Adds a new exception handler to the route class.
        :param exc_class: The type of exception to be handled.
        :param handler: A callable that is invoked when an exception of the specified
                        type is raised. May be sync or async.
        """
        cls.exception_handlers[exc_class] = handler

    @classmethod
    def _lookup_exception_handler(
        cls, exc: Exception
    ) -> Optional[
        Callable[[Request, Exception], Response | Coroutine[Any, Any, Response]]
    ]:
        """
        Finds the appropriate exception handler the specified exception type.
        :param exc: The exception that was raised.
        :return: An exception handler, or ``None`` if no appropriate handler has been
                 registered.
        """
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
