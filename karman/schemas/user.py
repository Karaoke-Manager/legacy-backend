from typing import Any, Dict

from pydantic import Field

from .base import BaseModelSchema


class User(BaseModelSchema):
    """
    A user represents a human being accessing the API through a client application.
    """

    id: str = Field(
        ..., title="ID", description="A unique ID for the user.", min_length=1
    )
    username: str = Field(..., description="The unique name of the user.", min_length=1)
    preferences: Dict[str, Any] = Field(
        {},
        description="Arbitrary user preferences that can be used by client "
        "applications. Keys in this dictionary should correspond to unique client "
        "identifiers (e.g. a reverse DNS identifier).",
    )
    public_preferences: Dict[str, Any] = Field(
        {},
        title="Public Preferences",
        description="Arbitrary user preferences that can be used by client "
        "applications. Keys in this dictionary should correspond to unique client "
        "identifiers (e.g. a reverse DNS identifier). In contrast to the `preferences`"
        "these preferences can be seen by other users.",
    )
