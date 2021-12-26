__all__ = [
    "OAuth2Token",
    "OAuth2ResponseType",
    "OAuth2AuthorizationRequest",
    "OAuth2GrantType",
    "OAuth2TokenRequestForm",
    "OAuth2TokenResponse",
    "OAuth2Error",
    "OAuth2ErrorResponse",
]

from datetime import timedelta
from enum import Enum
from typing import Optional

from fastapi import Form, Query
from pydantic import BaseModel, Field, HttpUrl

from karman.config import settings
from karman.oauth import Scope

OAuth2Token = str


class OAuth2ResponseType(str, Enum):
    """Possible values for the OAuth 2 response type."""

    CODE = "code"
    TOKEN = "token"


# Note: This schema is compliant with the OAuth 2 authorize endpoint schema. We
# currently do not implement the OAuth spec completely but may do so in the future.
class OAuth2AuthorizationRequest:
    def __init__(
        self,
        connection: str = Query(
            ...,
            description="The name of the external login provider, as configured in the "
            "application's settings.",
            example="google",
        ),
        client_id: str = Query(
            None,
            description="The application's client id. This value is required by the "
            "spec but is currently ignored.",
        ),
        response_type: OAuth2ResponseType = Query(
            ...,
            description="Identifies the type of OAuth flow to be used. Currently only "
            "`code` flows are supported.",
            example=OAuth2ResponseType.CODE,
        ),
        redirect_uri: HttpUrl = Query(
            ...,
            description="The URL where we redirect to after the login process completes.",
            example="https://example.com/oauth-callback",
        ),
        scope: str = Query(
            "", description="A list of scopes that your application requests."
        ),
        state: Optional[str] = Query(
            None,
            description="An arbitrary string value that allows you to correlate the login "
            "request with the response.",
        ),
    ):
        self.connection = connection
        self.client_id = client_id
        self.response_type = response_type
        self.redirect_uri = redirect_uri
        self.scope = [Scope(v) for v in scope.split()]
        self.state = state


class OAuth2GrantType(str, Enum):
    """Possible values for OAuth 2 grant type"""

    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    IMPLICIT = "implicit"
    PASSWORD = "password"
    REFRESH_TOKEN = "refresh_token"


# Note: This schema is compliant with the OAuth 2 token endpoint schema. We currently do
# not implement the OAuth spec completely but may do so in the future.
class OAuth2TokenRequestForm:
    """
    This subclass of `OAuth2PasswordRequestForm` can be used exactly as the original. It
    only adds OpenAPI documentation.
    """

    def __init__(
        self,
        grant_type: OAuth2GrantType = Form(
            ...,
            description="The OAuth 2.0 grant type.",
            example=OAuth2GrantType.PASSWORD,
        ),
        scope: str = Form("", description="The OAuth scopes that are being requested."),
        client_id: str = Form(
            None,
            description="Unique identifier of the client application.",
        ),
        client_secret: Optional[str] = Form(
            None,
            description="The client secret value. This value identifies the client.",
        ),
        # Password Flow
        username: Optional[str] = Form(
            ...,
            description="The username of the user that attempts to log in. Required if "
            "`grant_type` is `password`.",
            example="johndoe",
        ),
        password: Optional[str] = Form(
            ...,
            description="The plain text password of the user `username`. Required if "
            "`grant_type` is `password`.",
            example="hunter2",
        ),
        # Authorization Code Flow
        code: Optional[str] = Form(
            None,
            description="The authorization code received in the redirect uri. Required "
            "if `grant_type` is `authorization_code`.",
        ),
        redirect_uri: Optional[HttpUrl] = Form(
            None,
            description="The redirect URI of the client application, where it received "
            "the authorization code. Required if `grant_type` is `authorization_code`.",
        ),
        code_verifier: Optional[str] = Form(
            None,
            description="Used for PKCE support with the `authorization_code` grant "
            "type. This parameter is currently not used.",
        ),
        # Refresh Token
        refresh_token: Optional[str] = Form(
            None,
            description="The refresh token. Required if `grant_type` is `refresh_"
            "token`.",
        ),
    ):
        self.grant_type = grant_type
        self.scopes = [Scope(v) for v in scope.split()]
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.code = code
        self.redirect_uri = redirect_uri
        self.code_verifier = code_verifier
        self.refresh_token = refresh_token


class OAuth2TokenResponse(BaseModel):
    """A response from the OAuth 2.0 Token endpoint returning a token."""

    access_token: OAuth2Token = Field(
        ...,
        description="The access token string as issued by the authorization server.",
    )
    token_type: str = Field(
        "Bearer",
        description="The type of token this is, typically just the string `Bearer`",
        example="Bearer",
    )
    expires_in: Optional[timedelta] = Field(
        ...,
        description="The number of seconds the token is valid for. If no expiry time is"
        " returned the token may still expire after some time.",
        example=3600,
    )
    refresh_token: Optional[OAuth2Token] = Field(
        None,
        description="The server may return a refresh token that can be used to request "
        "a new access token after this one expires.",
    )
    scope: Optional[str] = Field(
        None,
        description="The scope that was granted to the token. May be omitted if "
        "the granted scopes are identical to the requested scopes.",
    )

    class Config:
        validate_all = settings.debug
        validate_assignment = settings.debug


class OAuth2Error(str, Enum):
    """Possible error code for OAuth 2 authentication."""

    INVALID_REQUEST = "invalid_request"
    INVALID_CLIENT = "invalid_client"
    INVALID_GRANT = "invalid_grant"
    INVALID_SCOPE = "invalid_scope"
    UNAUTHORIZED_CLIENT = "unauthorized_client"
    UNSUPPORTED_GRANT_TYPE = "unsupported_grant_type"


class OAuth2ErrorResponse(BaseModel):
    """A response from the OAuth 2.0 token endpoint returning an error."""

    error: OAuth2Error = Field(
        ...,
        description="The type of error that occurred.",
        example=OAuth2Error.INVALID_REQUEST,
    )
    error_description: Optional[str] = Field(
        None,
        description="A detailed description of the error.",
        example="Request was missing the 'redirect_uri' parameter.",
    )
    error_uri: Optional[HttpUrl] = Field(
        None,
        description="A URI related to the error or a possible solution.",
        example="https://example.com/docs/access_token",
    )

    class Config:
        validate_all = settings.debug
        validate_assignment = settings.debug
