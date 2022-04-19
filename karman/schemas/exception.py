from typing import Any, Optional

from pydantic import Field

from karman.schemas.base import BaseSchema


class ErrorSchema(BaseSchema):
    code: str = Field(..., description="A code identifying the type of error.")
    message: str = Field(
        ...,
        description="A descriptive error message. This message is not meant to be "
        "displayed to the end user.",
    )
    detail: Optional[Any] = Field(None, description="Additional data for this error.")
