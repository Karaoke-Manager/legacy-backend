from typing import List

from pydantic import AnyUrl

from karman.schemas.base import BaseSchema


class UploadServerInfo(BaseSchema):
    protocols: List[str]
    url: AnyUrl


class Info(BaseSchema):
    upload_servers: List[UploadServerInfo]