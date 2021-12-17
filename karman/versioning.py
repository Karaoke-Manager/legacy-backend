from typing import Any, Callable, Dict, Tuple, TypeVar

CallableT = TypeVar("CallableT", bound=Callable[..., Any])


def version(
    major: int, minor: int = 0, deprecated: bool = None
) -> Callable[[CallableT], CallableT]:
    """
    Marks an endpoint as available in a specific API version.
    :param major: The major API version.
    :param minor: The minor API version.
    :param deprecated: Whether this endpoint is deprecated in this version of
    the API. By default the deprecation value of the endpoint is used.
    """

    def decorator(func: CallableT) -> CallableT:
        versions: Dict[Tuple[int, int], bool] = getattr(func, "_api_versions", {})
        versions[(major, minor)] = deprecated
        func._api_versions = versions  # type: ignore
        return func

    return decorator
