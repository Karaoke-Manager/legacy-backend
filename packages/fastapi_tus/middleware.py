__all__ = ["HTTPMethodOverrideMiddleware"]

import re
from typing import List, Optional

from starlette.datastructures import Headers
from starlette.middleware import Middleware
from starlette.types import ASGIApp, Receive, Scope, Send


class HTTPMethodOverrideMiddleware(Middleware):
    def __init__(self, app: ASGIApp, paths: Optional[List[str]] = None) -> None:
        super().__init__(HTTPMethodOverrideMiddleware, paths=paths)
        self.app = app
        self.paths = paths

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] in ("http", "websocket"):
            headers = Headers(scope=scope)
            if "X-HTTP-Method-Override" in headers:
                if any(re.match(pattern, scope["path"]) for pattern in self.paths):
                    scope["method"] = headers["X-HTTP-Method-Override"].upper()
        await self.app(scope, receive, send)
