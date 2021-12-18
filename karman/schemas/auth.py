from datetime import timedelta
from enum import Enum
from typing import Optional

import fastapi.security
from fastapi import Form
from pydantic import BaseModel, Field

from karman.config import app_config

OAuth2Token = str


class OAuth2TokenResponse(BaseModel):
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
        validate_all = app_config.debug
        validate_assignment = app_config.debug


class OAuth2Error(str, Enum):
    """Possible error code for OAuth 2 authentication."""

    invalid_request = "invalid_request"
    invalid_client = "invalid_client"
    invalid_grant = "invalid_grant"
    invalid_scope = "invalid_scope"
    unauthorized_client = "unauthorized_client"
    unsupported_grant_type = "unsupported_grant_type"


class OAuth2ErrorResponse(BaseModel):
    error: OAuth2Error = Field(
        ...,
        description="The type of error that occurred.",
        example=OAuth2Error.invalid_request,
    )
    error_description: Optional[str] = Field(
        None,
        description="A detailed description of the error.",
        example="Request was missing the 'redirect_uri' parameter.",
    )
    error_uri: Optional[str] = Field(
        None,
        description="A URI related to the error or a possible solution.",
        example="See the full API docs at https://example.com/docs/access_token",
    )

    class Config:
        validate_all = app_config.debug
        validate_assignment = app_config.debug


class OAuth2PasswordRequestForm(fastapi.security.OAuth2PasswordRequestForm):
    """
    This subclass of `OAuth2PasswordRequestForm` can be used exactly as the original. It
    only adds OpenAPI documentation.
    """

    def __init__(
        self,
        grant_type: str = Form(
            ...,
            regex="password",
            description="The OAuth 2.0 grant type. Must be `password`.",
            example="password",
        ),
        username: str = Form(
            ...,
            description="The username of the user that attempts to log in.",
            example="johndoe",
        ),
        password: str = Form(
            ...,
            description="The plain text password of the user `username`.",
            example="hunter2",
        ),
        scope: str = Form("", description="The OAuth scopes that are being requested."),
        client_id: Optional[str] = Form(
            None,
            description="Optionally an OAuth client ID of the application attempting "
            "the sign in.",
        ),
        client_secret: Optional[str] = Form(
            None,
            description="Optionally an OAuth client secret of the application "
            "attempting the sing in.",
        ),
    ):
        super().__init__(
            grant_type=grant_type,
            username=username,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
        )
