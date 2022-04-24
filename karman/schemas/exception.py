__all__ = ["ErrorSchema"]

from typing import Any, Optional

from pydantic import Field

from .base import BaseSchema


class ErrorSchema(BaseSchema):
    """
    This schema is used by the Karman API to indicate that a request could not be
    fulfilled.
    """

    code: str = Field(
        ..., description="A code identifying the type of error.", example="notFound"
    )
    message: str = Field(
        ...,
        description="A descriptive error message. This message is not meant to be "
        "displayed to the end user.",
        example="The requested item was not found.",
    )
    detail: Optional[Any] = Field(None, description="Additional data for this error.")
