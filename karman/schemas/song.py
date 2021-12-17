__all__ = ["Song", "SongKind"]

from enum import Enum
from typing import List, Optional

from pydantic import Field, HttpUrl, confloat, conint

from .base import BaseSchema


class SongKind(str, Enum):
    """Identifies a type of song."""

    ultrastar = "ultrastar"
    """UltraStar compatible songs."""


class Song(BaseSchema):
    """
    A `Song` represents a song in the Karman database.
    """

    id: int = Field(
        ..., title="ID", description="The unique ID of the song.", example=123
    )
    title: str = Field(
        ..., description="The title of the song.", example="Love The Way You Lie"
    )
    artist: str = Field(
        ..., description="The (main) artist of the song.", example="Eminem"
    )
    featured_artists: List[str] = Field(
        ...,
        title="Featured Artists",
        description="A (potentially empty) list of featured artists for this "
        "song. This list does not include the main artist.",
        example=["Rihanna"],
    )
    year: Optional[conint(gt=0)] = Field(
        None, description="The year the song was released.", example=2010
    )
    genre: Optional[str] = Field(
        None, description="The genre of the song.", example="Hip-Hop"
    )
    kind: SongKind = Field(
        SongKind.ultrastar,
        title="Kind",
        description="The kind of song. Currently only `ultrastar` songs are "
        "supported.",
        example=SongKind.ultrastar,
    )
    players: conint(ge=1) = Field(
        1,
        description="The number of players for this song. Currently only "
        "solos (`1` player) and duets (`2` players) are "
        "supported.",
        example=1,
    )
    # TODO: Should we include the song's lyrics here?
    duration: Optional[confloat(gt=0)] = Field(
        None,
        description="The duration of the song in seconds. Note that this "
        "value is **not** guaranteed to be an integer. If the "
        "song's duration is unknown this will be `null`",
        example=266,
    )
    golden_notes: bool = Field(
        ...,
        title="Golden Notes",
        description="A boolean value indicating whether the song contains "
        "golden notes.",
        example=True,
    )
    artwork_url: Optional[HttpUrl] = Field(
        None,
        title="Artwork URL",
        description="An URL pointing to the song's artwork or `null` if the "
        "song does not have one.",
        example="https://.../artwork",
    )
    background_url: Optional[HttpUrl] = Field(
        None,
        title="Background URL",
        description="An URL pointing to the song's background image or `null` "
        "if the song does not have one.",
        example="https://.../background",
    )
    audio_url: Optional[HttpUrl] = Field(
        None,
        title="Audio URL",
        description="An URL pointing to the song's audio file or `null` if the "
        "song does not have one.",
        example="https://.../audio",
    )
    video_url: Optional[HttpUrl] = Field(
        None,
        title="Video URL",
        description="An URL pointing to the song's video file or `null` if the "
        "song does not have one.",
        example="https://.../video",
    )
    average_rating: Optional[confloat(ge=0, le=10)] = Field(
        None,
        title="Average Rating",
        description="The average user rating for this song (a decimal between "
        "`0` and `10`) or `null` if there are no ratings yet.",
        example=8.2,
    )
