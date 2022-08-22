__all__ = ["router"]

from typing import List

from fastapi import APIRouter, Path
from fastapi.params import Depends
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.limit_offset import Params
from starlette.status import HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from karman import schemas
from karman.util.versioning import version

router = APIRouter(
    tags=["Songs"],
    responses={
        HTTP_403_FORBIDDEN: {
            "description": "The request does not have sufficient privileges to "
            "be executed."
        }
    },
)
detail_router = APIRouter(
    responses={
        HTTP_404_NOT_FOUND: {
            "description": "No song with the specified `id` was found."
        }
    }
)


@version(1)
@router.get(
    "/",
    summary="List Songs",
    response_model=LimitOffsetPage[schemas.Song],
    response_description="The request was executed successfully.",
)
async def get_songs(
    params: Params = Depends(),  # type: ignore
) -> List[schemas.Song]:
    """Lists all songs in the Karman library."""
    raise NotImplementedError


@version(1)
@detail_router.get(
    "/{id}",
    summary="Get Song Details",
    response_model=schemas.Song,
    response_description="The request was executed successfully.",
)
async def get_song(
    song_id: int = Path(..., alias="id", description="The ID of the song.", example=123)
) -> schemas.Song:
    """Returns the details of the song with ID `id`."""
    raise NotImplementedError


@version(1)
@detail_router.delete(
    "/{id}",
    summary="Delete A Song",
    status_code=HTTP_204_NO_CONTENT,
    response_description="The song was deleted successfully.",
)
async def delete_song(
    song_id: int = Path(
        ...,
        alias="id",
        description="The ID of the song that should be " "deleted.",
        example=123,
    )
) -> None:
    """Deletes a song from the Karman database."""
    raise NotImplementedError


router.include_router(detail_router)
