from fs import open_fs
from fs.base import FS
from fs.mountfs import MountFS
from funcy import cached_property
from pydantic import BaseModel, RedisDsn, AnyUrl


class TestConfig(BaseModel):
    redis: RedisDsn = None
    redis_offset: int = 1
    mongo: AnyUrl = None
    db_prefix: str = ""


class JWTConfig(BaseModel):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    issuer: str


class StorageConfig(BaseModel):
    class Config:
        keep_untouched = (cached_property,)

    library: str
    user_songs: str
    imports: str
    uploads: str

    @cached_property
    def library_fs(self) -> FS:
        return open_fs(self.library)

    @cached_property
    def user_songs_fs(self) -> FS:
        return open_fs(self.user_songs)

    @cached_property
    def imports_fs(self) -> FS:
        return open_fs(self.imports)

    @cached_property
    def uploads_fs(self) -> FS:
        return open_fs(self.uploads)

    @cached_property
    def filesystem(self):
        fs = MountFS()
        fs.mount("/library", self.library_fs)
        fs.mount("/user-songs", self.user_songs_fs)
        fs.mount("/imports", self.imports_fs)
        fs.mount("/uploads", self.uploads_fs)
        return fs
