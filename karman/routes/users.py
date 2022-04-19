from fastapi import APIRouter, Depends
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from karman import schemas
from karman.oauth import OAuth2Token, get_token
from karman.versioning import version

router = APIRouter(
    tags=["Users"],
    responses={
        HTTP_401_UNAUTHORIZED: {"description": "The request is not authenticated."},
        HTTP_403_FORBIDDEN: {
            "description": "The request does not have sufficient privileges to "
            "be executed."
        },
    },
)


@version(1)
@router.get(
    "/me",
    summary="Get the current user",
    response_model=schemas.User,
    response_description="Data about the current user.",
)
async def me(token: OAuth2Token = Depends(get_token)):
    """Returns information about the user that authenticated the request."""
    pass
