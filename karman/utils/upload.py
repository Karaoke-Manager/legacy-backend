import asyncio
import uuid
from typing import Callable, Awaitable, Optional

from aioredis import Redis
from fastapi import Depends

from fastapi_helpers import app_dependency
from karman.app import app
from karman.config import app_config
from .callback import CallbackChannel
from .redis import get_redis

UPLOADS_CHANNEL = "channel:uploads"


@app_dependency(app)
async def get_uploads_callback_channel():
    async with CallbackChannel(await get_redis(), UPLOADS_CHANNEL) as channel:
        yield channel


class UploadManager:
    UPLOADS_KEY = "uploads"

    def __init__(self,
                 redis: Redis = Depends(get_redis),
                 channel: CallbackChannel = Depends(get_uploads_callback_channel)):
        self.redis = redis
        self.channel = channel

    async def register_upload(self, callback: Callable[[Optional[str]], Awaitable], *args, **kwargs) -> str:
        uid = str(uuid.uuid4())
        await asyncio.gather(*[
            self.channel.register_callback(uid, callback, *args, **kwargs),
            self.redis.hset(self.UPLOADS_KEY, uid, "")
        ])
        return uid

    async def begin_upload(self, uid: str):
        state = await self.redis.hget(UploadManager.UPLOADS_KEY, uid)
        if state is None or state.decode() != "":
            raise LookupError
        await self.redis.hset(self.UPLOADS_KEY, uid, "uploading")

    async def end_upload(self, uid: str, file: Optional[str]):
        await self.channel.dispatch_callback(uid, file)

    @staticmethod
    async def clean():
        # TODO: Schedule this function to run from time to time
        # TODO: Remove files that are older than some expiration date.
        await asyncio.gather(*[
            server.clean() for server in app_config.upload_servers
        ])
