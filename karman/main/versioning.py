import copy
from typing import Callable, Dict, Optional, Tuple, Union, cast

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from starlette.routing import Route


def strict_version_selector(
    major: int, minor: Optional[int] = None
) -> Callable[[Route], Optional[Route]]:
    def selector(route: Route) -> Optional[Route]:
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
    selector: Callable[[Route], Optional[Route]] = strict_version_selector,
):
    if isinstance(source, FastAPI):
        source = source.router
    if isinstance(destination, FastAPI):
        destination = destination.router

    for route in source.routes:
        new_route = selector(route)
        if new_route is not None:
            destination.routes.append(new_route)
