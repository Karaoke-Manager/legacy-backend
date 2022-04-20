__all__ = ["router"]

from typing import Optional

from fastapi import APIRouter, Depends, Query, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute, Request
from ormar import NoMatch
from pydantic import HttpUrl
from starlette.responses import JSONResponse, RedirectResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from karman import oauth
from karman.exceptions import HTTPException
from karman.models import User
from karman.oauth import Scope, Scopes, create_access_token, verify_password
from karman.schemas.oauth import (
    OAuth2AuthorizationRequest,
    OAuth2ErrorResponse,
    OAuth2TokenRequest,
    OAuth2TokenResponse,
)
from karman.util.exception import ErrorHandlingAPIRoute
from karman.versioning import version


class OAuthAPIRoute(ErrorHandlingAPIRoute):
    pass


@OAuthAPIRoute.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exception: HTTPException) -> Response:
    content = {
        "error": exception.error_code,
        "error_description": exception.message,
    }
    if exception.detail:
        content["error_uri"] = exception.detail
    return JSONResponse(status_code=exception.status_code, content=content)


@OAuthAPIRoute.exception_handler(RequestValidationError)
async def handle_request_validation_error(
    request: Request, exception: RequestValidationError
) -> Response:
    # We just return info about one validation error
    try:
        error = exception.errors()[0]
        field = error["loc"][-1]
        message = error["msg"]
        if field == "scope":
            return JSONResponse(
                status_code=HTTP_400_BAD_REQUEST,
                content={"error": "invalid_scope", "error_description": message},
            )
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={
                "error": "invalid_request",
                "error_description": f"Error for parameter '{field}': {message}",
            },
        )
    except IndexError:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={
                "error": "invalid_request",
                "error_description": "The request was formatted incorrectly.",
            },
        )


router = APIRouter(
    tags=["Authentication"],
    route_class=OAuthAPIRoute,
    responses={HTTP_422_UNPROCESSABLE_ENTITY: {"include_in_schema": False}},
)


@version(1)
@router.post(
    f"/{oauth.token_url}",
    summary="Get an access token",
    response_model=OAuth2TokenResponse,
    response_model_exclude_none=True,
    response_description="The response to a successful request contains an "
    "`access_token` and optionally a `refresh_token`.",
    responses={
        HTTP_400_BAD_REQUEST: {
            "model": OAuth2ErrorResponse,
            "description": """
An incorrectly formatted request will result in an error. Possible error codes are:

- `invalid_request`: The request was not formatted correctly.
- `invalid_grant`: The authorization code is invalid or expired.
- `invalid_scope`: One of the scopes requested is invalid.
- `unauthorized_client`: The client is not authorized to use the requested grant type.
- `unsupported_grant_type`: The requested grant type is not available.
""",
        },
        HTTP_401_UNAUTHORIZED: {
            "model": OAuth2ErrorResponse,
            "description": "If the specified `client_id` or `client_secret` are "
            "invalid. The returned error code will be `invalid_client` in this case.",
        },
    },
)
async def token(
    response: Response,
    data: OAuth2TokenRequest = Depends(),
) -> OAuth2TokenResponse:
    """
    This endpoint implements the [OAuth 2.0 Token Endpoint](
    https://www.oauth.com/oauth2-servers/access-tokens/access-token-response/). If
    authentication succeeds, a token is returned granting access to the API.
    """
    response.headers["Cache-Control"] = "no-store"
    if data.grant_type == "password":
        if not data.username or not data.password:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                error_code="invalid_request",
                message="username and password required.",
            )
        try:
            user = await User.objects.get(username=data.username)
            if not verify_password(data.password, user.password):
                # technically not the correct exception but works well here
                raise NoMatch
            # TODO: Use and validate client_id
            client_id = "fake"
            # TODO: Use correct scopes
            scopes = Scopes({Scope.ALL})
            bearer, claims = create_access_token(user, client_id, scopes)
            return OAuth2TokenResponse(
                access_token=bearer,
                expires_in=claims.valid_until - claims.issued_at,
                scope=claims.scope,
            )
        except NoMatch:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                error_code="invalid_request",
                message="username and password do not match.",
            )
    else:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            error_code="unsupported_grant_type",
            message="This grant type is currently not supported.",
        )


def authorize_callback(
    code: Optional[str] = Query(
        None, description="The authorization code returned by the API."
    ),
    state: Optional[str] = Query(
        None,
        description="The state value provided on the initial authorization request.",
    ),
    error: Optional[str] = Query(
        None,
        description="""
An error code identifying what kind of error occurred. Possible values are:

- `access_denied`: The user or authorization server denied the request.
- `unauthorized_client`: The client is not allowed to request an authorization code
  using this method.
- `unsupported_response_type`: Obtaining an authorization code using this method is not
  supported.
- `server_error`: Some kind of internal server error occurred.
- `temporarily_unavailable`: The server is currently undergoing maintenance.
""",
    ),
    error_description: Optional[str] = Query(
        None, description="A detailed description of what went wrong."
    ),
    error_uri: Optional[HttpUrl] = Query(
        None, description="A URL containing additional information about the error."
    ),
) -> None:
    """
    The user will be redirected to this URL after the authentication process completes.
    Use the provided `code` and `state` to acquire a token.
    """
    # This function is intentionally empty. It only servers documentation purposes.
    pass


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
            responses={HTTP_422_UNPROCESSABLE_ENTITY: {"include_in_schema": False}},
        )
    ],
    responses={
        HTTP_400_BAD_REQUEST: {
            "model": OAuth2ErrorResponse,
            "description": """
An incorrectly formatted request will result in an error. Possible error codes are:

- `invalid_request`: The request was not formatted correctly.
- `unauthorized_client`: The client is not allowed to request an authorization code
  using this method.
- `unsupported_response_type`: Obtaining an authorization code using this method is not
  supported.
- `invalid_scope`: The requested scope is invalid or unknown.
""",
        },
        HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": OAuth2ErrorResponse,
            "description": "An internal server error occurred. The error code is "
            "`server_error`.",
        },
        HTTP_503_SERVICE_UNAVAILABLE: {
            "model": OAuth2ErrorResponse,
            "description": "The server is undergoing maintenance. The error code is "
            "`temporarily_unavailable`.",
        },
    },
)
async def authorize(
    request: OAuth2AuthorizationRequest = Depends(),
) -> RedirectResponse:
    """
    Redirects to an authentication provider as specified by `connection`. The provider
    then performs authentication and redirects back to the specified `redirect_uri` with
    a `code` in the request. The `code` can then be exchanged with an access token.
    """
    # TODO: Maybe pass additional parameters to the Auth backend?
    raise NotImplementedError
