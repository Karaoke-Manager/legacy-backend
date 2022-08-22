__all__ = [
    "OAuth2AccessToken",
    "OAuth2ResponseType",
    "OAuth2AuthorizationRequest",
    "OAuth2TokenRequest",
    "OAuth2TokenResponse",
    "OAuth2ErrorResponse",
]

from datetime import timedelta
from enum import Enum
from typing import Optional

from fastapi import Form, Header, Query
from pydantic import BaseModel, Field, HttpUrl

from ..oauth import BearerToken, OAuth2AccessToken, Scopes
from ..util.auth import decode_basic_auth


class OAuth2ResponseType(str, Enum):
    """Possible values for the OAuth 2 response type."""

    CODE = "code"
    TOKEN = "token"


# Note: This schema is compliant with the OAuth 2 authorize endpoint schema. We
# currently do not implement the full OAuth spec completely but may do so in the future.
class OAuth2AuthorizationRequest:
    """
    Request schema for the [OAuth 2.0 /authorize endpoint](
    https://www.oauth.com/oauth2-servers/authorization/the-authorization-request/). This
    class is intended to be used as a FastAPI dependency.

    The request object can be used for all flows that use the /authorize endpoint. Note
    however that this class does not perform any semantic validation on the provided
    parameters. Depending on the provided ``response_type`` you might want to ensure
    that certain parameters are set.
    """

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
            description="The URL where we redirect to after the login process "
            "completes.",
            example="https://example.com/oauth-callback",
        ),
        scope: Optional[Scopes] = Query(
            None,
            description="A list of scopes that your application requests.",
        ),
        state: Optional[str] = Query(
            None,
            description="An arbitrary string value that allows you to correlate the "
            "login request with the response.",
        ),
    ):
        """
        Initializes the request object with the values provided by the request. Usually
        you do not need to call this method yourself but let FastAPI handle this via its
        dependency mechanism.
        """
        self.connection = connection
        self.client_id = client_id
        self.response_type = response_type
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.state = state


# Note: This schema is compliant with the OAuth 2 token endpoint schema. We currently do
# not implement the OAuth spec completely but may do so in the future.
class OAuth2TokenRequest:
    """
    Request schema for the [OAuth 2.0 /token endpoint(
    https://www.oauth.com/oauth2-servers/device-flow/token-request/). This class is
    intended to be used as a FastAPI dependency.

    The request object can be used for all flows that use the /token endpoint. Note
    however that this class does not perform any semantic validation on the provided
    parameters. Depending on the provided ``grant_type`` you might want to ensure
    that certain parameters are set.

    The request schema does understand two kinds of client authentication:
    - You can provide a ``client_id`` and ``client_secret`` in the request body along
      with all the other parameters.
    - You can provide the ``client_id`` and ``client_secret`` via HTTP Basic Auth. If
      any ``Authorization`` header is present it takes precedence over the values in the
      request body, even if it is not a valid Basic Auth header. If the
      ``Authorization`` header is not a valid HTTP Basic Auth header, the request is
      assumed to be unauthenticated (``client_id`` and ``client_secret`` are set to
      ``None``). No exception is raised in this case.
    """

    def __init__(
        self,
        grant_type: str = Form(
            ...,
            description="The OAuth 2.0 grant type.",
            example="authorization_code",
        ),
        scope: Optional[Scopes] = Form(
            None, description="The OAuth scopes that are being requested."
        ),
        authorization: Optional[str] = Header(
            None,
            description="The client id and client secret can be passed via HTTP basic "
            "auth. This takes precedence over parameters specified in the request "
            "body.",
        ),
        client_id: Optional[str] = Form(
            None,
            description="Unique identifier of the client application.",
        ),
        client_secret: Optional[str] = Form(
            None,
            description="The client secret value. This value identifies the client.",
        ),
        # Password Flow
        username: Optional[str] = Form(
            None,
            description="The username of the user that attempts to log in. Required if "
            "`grant_type` is `password`.",
            example="johndoe",
        ),
        password: Optional[str] = Form(
            None,
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
        """
        Initializes the request object with the values provided by the request. Usually
        you do not need to call this method yourself but let FastAPI handle this via its
        dependency mechanism.
        """
        self.grant_type = grant_type
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret
        if authorization:
            try:
                self.client_id, self.client_secret = decode_basic_auth(authorization)
            except ValueError:
                self.client_id = None
                self.client_secret = None
        self.username = username
        self.password = password
        self.code = code
        self.redirect_uri = redirect_uri
        self.code_verifier = code_verifier
        self.refresh_token = refresh_token


class OAuth2TokenResponse(BaseModel):
    """
    A response from the OAuth 2.0 Token endpoint returning a token. In case of an error
    this schema does not apply.
    """

    access_token: BearerToken = Field(
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
    refresh_token: Optional[BearerToken] = Field(
        None,
        description="The server may return a refresh token that can be used to request "
        "a new access token after this one expires.",
    )
    scope: Optional[Scopes] = Field(
        None,
        description="The scope that was granted to the token. May be omitted if "
        "the granted scopes are identical to the requested scopes.",
    )

    class Config:
        # Include the custom encoder here until this issue is solved:
        # https://github.com/samuelcolvin/pydantic/issues/951
        json_encoders = {Scopes: str}


class OAuth2ErrorResponse(BaseModel):
    """
    A response from the OAuth 2.0 token endpoint returning an error. In case of an error
    this schema does not apply.
    """

    error: str = Field(
        ...,
        description="The type of error that occurred.",
        example="invalid_request",
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
