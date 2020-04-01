import asyncio
import re
from typing import Optional, Dict, Tuple, Callable, Awaitable, Sequence, Mapping

from aioredis import Redis, Channel


class CallbackChannel:
    def __init__(self, redis: Redis, channel_name: str):
        assert redis is not None

        self.redis: Redis = redis
        self.channel_name = channel_name
        self.channel: Optional[Channel] = None
        self.task: Optional[asyncio.Task] = None
        self.callbacks: Dict[str, Tuple[Callable[..., Awaitable], Sequence, Mapping]] = {}

    def register_callback(self, cid: str, callback: Callable[..., Awaitable], *args, **kwargs):
        self.callbacks[cid] = (callback, args, kwargs)

    async def dispatch_callback(self, cid: str, data: Optional[str] = None):
        if data is None:
            await self.redis.publish(self.channel_name, cid)
        else:
            await self.redis.publish(self.channel_name, f"{cid}: {data}")

    async def invoke_callback(self, cid: str, data: Optional[str]):
        try:
            (callback, args, kwargs) = self.callbacks.pop(cid)
            await callback(data, *args, **kwargs)
        except KeyError:
            pass

    async def __aenter__(self):
        assert self.channel is None
        assert self.task is None

        self.channel, = await self.redis.subscribe(self.channel_name)
        self.task = asyncio.create_task(self._loop())

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        assert self.task
        assert self.channel

        await self.redis.unsubscribe(self.channel_name)
        await self.task
        self.channel = None
        self.task = None

    async def _loop(self):
        message: bytes
        async for message in self.channel.iter():
            match = re.match("^(?P<cid>[^:]+)(: (?P<data>.+))?$", message.decode())
            if not match:
                continue
            cid = match.group("cid")
            data = match.group("data")
            await self.invoke_callback(cid, data)
