from typing import Optional

from fastapi import APIRouter, Depends, Header, Response
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from karman.config import app_config
from karman.schemas.auth import (
    OAuth2ErrorResponse,
    OAuth2PasswordRequestForm,
    OAuth2TokenResponse,
)
from karman.versioning import version

router = APIRouter(tags=["Authentication"])


@version(1)
@router.post(
    f"/{app_config.oauth2_password_endpoint}",
    summary="Login with Username and Password",
    response_model=OAuth2TokenResponse,
    response_description="The response to a successful request contains an "
    "`access_token` and optionally a `refresh_token`.",
    responses={
        HTTP_400_BAD_REQUEST: {
            "model": OAuth2ErrorResponse,
            "description": "An incorrectly formatted request will result in an error.",
        },
        HTTP_401_UNAUTHORIZED: {
            "model": OAuth2ErrorResponse,
            "description": "If the specified `client_id` or `client_secret` are "
            "invalid. The returned error code will be `invalid_client` in this case.",
        },
    },
)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    authorization: Optional[str] = Header(
        None,
        description="You can supply the `client_id` and `client_secret` via HTTP Basic "
        "Auth instead of using the request body.",
    ),
) -> OAuth2TokenResponse:
    """
    Authenticates a user using `username` and`password`. This endpoint implements the
    [OAuth 2.0 Password Grant](
    https://www.oauth.com/oauth2-servers/access-tokens/password-grant/).
    """
    response.headers["Cache-Control"] = "no-store"
    raise NotImplementedError
