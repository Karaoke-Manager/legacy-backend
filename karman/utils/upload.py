import asyncio
import re
import uuid
from typing import Callable, Dict, Awaitable, Tuple, Sequence, Optional

from aioredis import Redis, Channel
from fastapi import Depends

from karman.config import app_config
from karman.utils.redis import redis


class UploadManager:
    UPLOADS_KEY = "uploads"
    UPLOADS_CHANNEL = "channel:uploads"

    callbacks: Dict[uuid.UUID, Tuple[Callable[[Optional[str]], Awaitable], Sequence]] = {}
    subscribed = False

    @staticmethod
    async def register_callback(uid: uuid.UUID,
                                callback: Tuple[Callable[[Optional[str]], Awaitable], Sequence],
                                redis_pool: Redis):
        assert callback is not None
        if not UploadManager.subscribed:
            UploadManager.subscribed = True
            channel, = await redis_pool.subscribe(UploadManager.UPLOADS_CHANNEL)
            asyncio.create_task(UploadManager.callback_loop(channel))
        UploadManager.callbacks[uid] = callback

    @staticmethod
    async def callback_loop(channel: Channel):
        message: bytes
        async for message in channel.iter():
            match = re.match("^(?P<uuid>[^:]+)(: (?P<file>.+))?$", message.decode())
            if not match:
                continue
            try:
                uid = uuid.UUID(match.group("uuid"))
                file = match.group("file")
                (callback, args) = UploadManager.callbacks.pop(uid)
                await callback(file, *args)
            except (ValueError, KeyError):
                pass

    def __init__(self, redis_pool: Redis = Depends(redis)):
        self.redis = redis_pool

    async def register_upload(self, callback: Callable[[Optional[str]], Awaitable], *args) -> uuid.UUID:
        uid = uuid.uuid4()
        await asyncio.gather(*[
            UploadManager.register_callback(uid, (callback, args), self.redis),
            self.redis.hset(self.UPLOADS_KEY, str(uid), "pending")
        ])
        return uid

    async def begin_upload(self, uid: [str, uuid.UUID]):
        exists = await self.redis.hget(UploadManager.UPLOADS_KEY, str(uid))
        if exists.decode() != "pending":
            raise LookupError
        await self.redis.hset(self.UPLOADS_KEY, str(uid), "in progress")

    async def end_upload(self, uid: str, file: Optional[str]):
        if file:
            await self.redis.publish(self.UPLOADS_CHANNEL, f"{uid}: {file}")
        else:
            await self.redis.publish(self.UPLOADS_CHANNEL, uid)

    @staticmethod
    async def clean():
        # TODO: Schedule this function to run from time to time
        # TODO: Remove files that are older than some expiration date.
        await asyncio.gather(*[
            server.clean() for server in app_config.upload_servers
        ])
