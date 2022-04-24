__all__ = ["HTTPException"]

from typing import Any, Dict, Optional

from fastapi import HTTPException as FastAPIHTTPException


class HTTPException(FastAPIHTTPException):
    """
    A custom subclass of FastAPI's ``HTTPException``.

    This class adds a field ``error_code`` making it possible to provide a
    machine-readable error detail in error responses.
    """

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.message = message

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return (
            f"{class_name}(status_code={self.status_code!r}, "
            f"error_code={self.error_code!r}, message={self.message!r}, "
            f"detail={self.detail!r})"
        )
