from typing import Callable, Awaitable, Dict, List

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


class CustomHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, add_headers: Dict[str, str] = None, remove_headers: List[str] = None):
        super().__init__(app)
        if add_headers is None:
            add_headers = {}
        self.add_headers = add_headers
        if remove_headers is None:
            remove_headers = []
        self.remove_headers = remove_headers

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        response = await call_next(request)
        for key in self.remove_headers:
            if key in response.headers:
                del response.headers[key]
        for (key, value) in self.add_headers.items():
            response.headers.setdefault(key, value)
        return response
