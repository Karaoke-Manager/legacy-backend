from fastapi import APIRouter, Depends, Security
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from karman import schemas
from karman.models import User
from karman.oauth import OAuth2AccessToken, Scope, get_access_token, get_user
from karman.schemas.exception import ErrorSchema
from karman.versioning import version

router = APIRouter(
    tags=["Users"],
    responses={
        HTTP_401_UNAUTHORIZED: {
            "model": ErrorSchema,
            "description": "The request is not authenticated.",
        },
        HTTP_403_FORBIDDEN: {
            "model": ErrorSchema,
            "description": "The request does not have sufficient privileges to "
            "be executed.",
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
async def me(user: User = Security(get_user, scopes=[Scope.SONGS])):
    """Returns information about the user that authenticated the request."""
    return user
