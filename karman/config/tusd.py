import asyncio
import os
from typing import Union, Dict, Sequence

from aioredis import Redis
from fastapi import FastAPI, APIRouter, Depends, Header, HTTPException
from jwt import PyJWTError
from pydantic import BaseModel, Field, validator
from starlette import status

from karman.config.upload import UploadServer
from karman.helpers.crypto import verify_jwt_token
from karman.utils import UploadManager, get_redis

__all__ = ["Tusd"]


class TusdStorageSchema(BaseModel):
    # Only the filestore is currently supported
    type: str = Field("filestore", const=True, alias="Type")
    path: str = Field(..., alias="Path")


class TusdUploadSchema(BaseModel):
    id: str = Field(None, alias="ID")
    metadata: Dict[str, str] = Field(..., alias="MetaData")
    storage: TusdStorageSchema = Field(None, alias="Storage")
    partial: bool = Field(..., alias="IsPartial")


class TusdRequestSchema(BaseModel):
    headers: Dict[str, str] = Field(..., alias="Header")

    @validator("headers", pre=True)
    def lowercase_headers(cls, value):
        if not isinstance(value, dict):
            return value
        else:
            return {key.lower(): value[0] for (key, value) in value.items() if len(value) > 0}


class TusdHookSchema(BaseModel):
    upload: TusdUploadSchema = Field(..., alias="Upload")
    request: TusdRequestSchema = Field(..., alias="HTTPRequest")


class Tusd(UploadServer):
    REDIS_KEY = "tusd"

    def __init__(self, url: str, hook_route: str = "/tusd", path_prefix: str = "/srv/tusd-data"):
        super().__init__(url)
        self.hook_route = hook_route
        self.path_prefix = path_prefix

    @property
    def upload_protocols(self) -> Sequence[str]:
        return "tus",

    def register_routes(self, app: Union[FastAPI, APIRouter]) -> None:
        # TODO: Document This Endpoint

        @app.post(self.hook_route, include_in_schema=False)
        async def process_hook(data: TusdHookSchema, hook_name: str = Header(...),
                               redis: Redis = Depends(get_redis),
                               uploader: UploadManager = Depends()):
            uid = data.request.headers.get("upload-id")
            if hook_name == "pre-create":
                # We only need to verify the authorization header in the
                # pre-create hook since ano other hook is non-blocking.
                try:
                    authorization = data.request.headers["authorization"]
                    verify_jwt_token(authorization[len("Bearer "):])
                except (KeyError, PyJWTError):
                    raise HTTPException(status.HTTP_401_UNAUTHORIZED)

                if not data.upload.partial:
                    if not uid:
                        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Upload-ID header missing")
                    try:
                        await uploader.begin_upload(uid)
                    except LookupError:
                        raise HTTPException(status.HTTP_428_PRECONDITION_REQUIRED,
                                            detail="Cannot create upload for specified id")
            elif hook_name == "post-create":
                await redis.hset(Tusd.REDIS_KEY, data.upload.id, uid)
            elif hook_name == "post-finish":
                uid = await redis.hget(Tusd.REDIS_KEY, data.upload.id)
                await redis.hdel(Tusd.REDIS_KEY, data.upload.id)
                file = os.path.relpath(data.upload.storage.path, self.path_prefix)
                await asyncio.gather(*[
                    redis.hdel(Tusd.REDIS_KEY, data.upload.id),
                    uploader.end_upload(uid.decode(), file)
                ])
            elif hook_name == "post-terminate":
                uid = await redis.hget(Tusd.REDIS_KEY, data.upload.id)
                await asyncio.gather(*[
                    redis.hdel(Tusd.REDIS_KEY, data.upload.id),
                    uploader.end_upload(uid.decode(), None)
                ])
                # TODO: Delete Files

    async def clean(self, uploader: UploadManager) -> None:
        pass
