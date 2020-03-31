from abc import ABC, abstractmethod
from typing import Union

from fastapi import APIRouter, FastAPI

from karman.utils.upload import UploadManager

__all__ = ["UploadServer"]


class UploadServer(ABC):

    def __init__(self, url: str):
        self._url = url

    @property
    def url(self) -> str:
        return self._url

    @property
    @abstractmethod
    def server_type(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def register_routes(self, app: Union[FastAPI, APIRouter]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def clean(self, uploader: UploadManager) -> None:
        raise NotImplementedError
