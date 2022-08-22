import copy
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar, Union, cast

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from starlette.routing import BaseRoute

CallableT = TypeVar("CallableT", bound=Callable[..., Any])


def version(
    major: int, minor: int = 0, deprecated: Optional[bool] = None
) -> Callable[[CallableT], CallableT]:
    """
    Marks an endpoint as available in a specific API version.
    :param major: The major API version.
    :param minor: The minor API version.
    :param deprecated: Whether this endpoint is deprecated in this version of
    the API. By default, the deprecation value of the endpoint is used.
    """

    def decorator(func: CallableT) -> CallableT:
        versions: Dict[Tuple[int, int], Optional[bool]] = getattr(
            func, "_api_versions", {}
        )
        versions[(major, minor)] = deprecated
        func._api_versions = versions  # type: ignore
        return func

    return decorator


def strict_version_selector(
    major: int, minor: Optional[int] = None
) -> Callable[[BaseRoute], Optional[BaseRoute]]:
    def selector(route: BaseRoute) -> Optional[BaseRoute]:
        api_route = cast(APIRoute, route)
        versions: Dict[Tuple[int, int], bool] = getattr(
            api_route.endpoint, "_api_versions", {}
        )
        for route_major, route_minor in reversed(sorted(versions.keys())):
            if major != route_major:
                continue
            if minor is not None and minor != route_minor:
                continue
            new_route = copy.deepcopy(api_route)
            deprecated = versions[(route_major, route_minor)]
            if deprecated is not None:
                new_route.deprecated = deprecated
            return new_route
        return None

    return selector


def select_routes(
    source: Union[FastAPI, APIRouter],
    destination: Union[FastAPI, APIRouter],
    selector: Callable[[BaseRoute], Optional[BaseRoute]],
) -> None:
    """
    Filters the routes from the ``source`` router by applying a ``selector``. Matching
    routes will be added to the ``destination`´ router.
    """
    if isinstance(source, FastAPI):
        source = source.router
    if isinstance(destination, FastAPI):
        destination = destination.router

    for route in source.routes:
        new_route = selector(route)
        if new_route is not None:
            destination.routes.append(new_route)
