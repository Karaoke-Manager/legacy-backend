from datetime import timedelta
from typing import List, Dict, Tuple, Literal, Union

from motor_odm import Document

Syllable = Tuple[Literal[':', 'F', '*'], int, int, int, str]
LineBreak = Tuple[Literal['-'], int]


class Song(Document):
    class Meta:
        collection = "songs"

    title: str
    artist: str
    featured_artists: List[str] = []
    genre: str = None
    edition: str = None

    metadata: Dict[str, str]

    duration: timedelta
    gap: timedelta
    bpm: float

    audio_file: str = None
    cover_file: str = None
    video_file: str = None
    background_file: str = None

    relative: bool
    lyrics: str

    syllables: List[Union[Syllable, LineBreak]]

    @property
    def has_audio(self) -> bool:
        return bool(self.audio_file)

    @property
    def has_cover(self) -> bool:
        return bool(self.cover_file)

    @property
    def has_video(self) -> bool:
        return bool(self.video_file)

    @property
    def has_background(self) -> bool:
        return bool(self.background_file)


class Duet(Song):
    lyrics2: str
    syllables2: List[Union[Syllable, LineBreak]]
