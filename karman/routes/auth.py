__all__ = ["router"]

from fastapi import APIRouter, Depends, Query, Response
from fastapi.routing import APIRoute
from starlette.responses import RedirectResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from karman import oauth
from karman.schemas.auth import (
    OAuth2AuthorizationRequest,
    OAuth2ErrorResponse,
    OAuth2TokenRequestForm,
    OAuth2TokenResponse,
)
from karman.versioning import version

router = APIRouter(
    tags=["Authentication"],
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


# Note: This endpoint is intentionally designed to be compatible with the OAuth token
# flows. Currently no such flow is implemented but may be in the future without breaking
# this API.
@version(1)
@router.post(
    f"/{oauth.token_url}",
    summary="Login with Username and Password",
    response_model=OAuth2TokenResponse,
    response_description="The response to a successful request contains an "
    "`access_token` and optionally a `refresh_token`.",
)
async def token(
    response: Response,
    form_data: OAuth2TokenRequestForm = Depends(),
) -> OAuth2TokenResponse:
    """
    Authenticates a user using `username` and`password`. This endpoint implements the
    [OAuth 2.0 Password Grant](
    https://www.oauth.com/oauth2-servers/access-tokens/password-grant/).
    """
    response.headers["Cache-Control"] = "no-store"
    raise NotImplementedError


def authorize_callback(
    code: str = Query(..., description="The authorization code returned by the API."),
    state: str = Query(
        ...,
        description="The state value provided on the initial authorization request.",
    ),
) -> None:
    """
    The user will be redirected to this URL after the authentication process completes.
    Use the provided `code` and `state` to acquire a token.
    """
    # This function is intentionally empty. It only servers documentation purposes.
    pass


# Note: This endpoint is intentionally designed to be compatible with the OAuth token
# flows. Currently no such flow is implemented but may be in the future without breaking
# this API.
@version(1)
@router.get(
    f"/{oauth.authorize_url}",
    summary="Login with an External IdP",
    response_class=RedirectResponse,
    response_description="You will be redirected to the IdP's authentication pages.",
    callbacks=[
        APIRoute(
            "{redirect_uri}",
            endpoint=authorize_callback,
            methods=["GET"],
            name="Callback URL",
            summary="Handle the response from the IdP.",
            response_class=Response,
            response_description="The client application defines the behavior of the "
            "callback URL. Its status code has no meaning for the API or the IdP.",
            responses={422: {}},
        )
    ],
)
async def authorize(
    request: OAuth2AuthorizationRequest = Depends(),
) -> RedirectResponse:
    """
    Redirects at an external authentication provider as specified by `connection`. The
    external provider then performs authentication and redirects back to the specified
    `redirect_uri` with a `code` in the request. The `code` can then be exchanged with
    an access token.
    """
    # TODO: Maybe pass additional parameters to the Auth backend?
    raise NotImplementedError
