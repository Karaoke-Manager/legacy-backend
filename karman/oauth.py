import uuid
from datetime import datetime
from enum import Enum
from functools import lru_cache
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    Optional,
    Set,
    Tuple,
    TypeAlias,
    Union,
)

from fastapi import Depends, Request
from fastapi.openapi.models import (
    OAuthFlowAuthorizationCode,
    OAuthFlowPassword,
    OAuthFlows,
)
from fastapi.security import OAuth2, SecurityScopes
from fastapi.security.utils import get_authorization_scheme_param
from jose import ExpiredSignatureError, JWTError, jwt
from ormar import NoMatch
from passlib.context import CryptContext
from pydantic import BaseModel, Field, ValidationError, validator
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from karman.config import settings
from karman.exceptions import HTTPException
from karman.models import User

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, DictStrAny, MappingIntStrAny

BearerToken: TypeAlias = str
OAuth2ClientID: TypeAlias = str


class Scope(str, Enum):
    @classmethod
    @lru_cache
    def all(cls) -> Dict[str, str]:
        return {scope.value: scope.description for scope in Scope}

    # Include this to help mypy detect the description field
    description: str

    def __new__(cls, value: str, description: str = "") -> "Scope":
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        if " " in value:
            raise ValueError("Scope values may not contain spaces.")
        if '"' in value:
            raise ValueError('Scope values may not contain a literal "')
        return obj

    def __repr__(self):
        return f"{self.__class__.__name__}.{self._name_}"

    ALL = ("all", "Includes all other scopes. Use with caution.")
    SONGS = ("songs", "Allow full access to songs.")
    READ_SONGS = ("songs:read", "Allow read access to songs.")
    # TODO: Add more scopes


class Scopes(Set[Scope]):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: dict):
        field_schema.clear()
        field_schema["type"] = "string"

    @classmethod
    def validate(cls, value: Any):
        if isinstance(value, str):
            return cls(Scope(v) for v in value.split(" "))
        elif isinstance(value, Iterable):
            return cls(Scope(v) for s in value for v in s.split(" "))
        raise TypeError("string required")

    def __repr__(self):
        return "{" + ", ".join(self) + "}"

    def __str__(self):
        return self.serialize()

    def serialize(self):
        return " ".join(self)


class OAuth2AccessToken(BaseModel):
    id: uuid.UUID = Field(..., alias="jti", description="A unique ID for this token.")
    issuer: str = Field(
        settings.jwt_issuer,
        alias="iss",
        description="An identification of who issued the token.",
    )
    subject: str = Field(
        ..., alias="sub", description="The entity identified by this token."
    )
    issued_at: datetime = Field(
        default_factory=datetime.utcnow,
        alias="iat",
        description="The UTC timestamp at which the token was issued.",
    )
    valid_until: datetime = Field(
        None,
        alias="exp",
        description="The UTC timestamp until this token is valid.",
    )
    username: Optional[str] = Field(
        None, description="The username of the user identified by this token."
    )
    client_id: str = Field(
        ..., description="The ID of the client acting on behalf of the user."
    )
    scope: Scopes = Field(..., description="Scopes associated with this token.")

    @validator("valid_until")
    def __validate_expiration(cls, v, values, **kwargs):
        if v is not None:
            return v
        if "issued_at" in values:
            issued_at = values["issued_at"]
            return issued_at + settings.jwt_validity_period
        raise ValueError("issued_at or valid_until must be specified.")

    def dict(
        self,
        *,
        include: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        exclude: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        encode: bool = False,
    ) -> "DictStrAny":
        data = super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias or encode,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
        if encode:
            data["jti"] = str(self.id)
            data["scope"] = str(self.scope)
        return data

    class Config:
        validate_all = settings.debug
        validate_assignment = settings.debug
        allow_population_by_field_name = True
        # Include the custom encoder here until this issue is solved:
        # https://github.com/samuelcolvin/pydantic/issues/951
        json_encoders = {Scopes: str}


token_url = "token"
authorize_url = "authorize"


class OAuth2Bearer(OAuth2):
    async def __call__(self, request: Request) -> Optional[BearerToken]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    error_code="unauthenticated",
                    message="The request needs to be authorized with a bearer token.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth_scheme = OAuth2Bearer(
    scheme_name="OAuth 2",
    description="Authenticate using one of the OAuth 2 flows.",
    # TODO: Allow configuration of enabled flows?
    flows=OAuthFlows(
        password=OAuthFlowPassword(tokenUrl=token_url, scopes=Scope.all()),
        authorizationCode=OAuthFlowAuthorizationCode(
            tokenUrl=token_url, authorizationUrl=authorize_url, scopes=Scope.all()
        ),
    ),
)


@lru_cache
def get_crypt_context():
    """
    Returns the password `CryptContext` used to hash passwords.
    """
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    context = get_crypt_context()
    return context.hash(password)


def verify_password(password, pw_hash):
    context = get_crypt_context()
    return context.verify(password, pw_hash)


def create_access_token(
    user: User, client_id: OAuth2ClientID, scope: Scopes
) -> Tuple[BearerToken, OAuth2AccessToken]:
    token = OAuth2AccessToken(
        id=uuid.uuid4(),
        subject=f"user:{user.id}",
        username=user.username,
        client_id=client_id,
        scope=scope,
    )
    return (
        jwt.encode(
            token.dict(encode=True), settings.jwt_secret_key, settings.jwt_algorithm
        ),
        token,
    )


async def get_access_token(
    scopes: SecurityScopes,
    token: BearerToken = Depends(oauth_scheme),
) -> OAuth2AccessToken:
    """
    This function is intended to be used as a FastAPI dependency. It fetches the access
    token from the request, validates and parses it and returns its claims in a pydantic
    model.

    :param scopes: Scopes required for the current request.
    :param token: The bearer token as specified by the user in the request.
    :return: The claims of the validated access token.
    :raises HTTPException: If the token is not present or invalid.
    """

    # Make sure that all requested scopes are valid scopes. It is a programmer error to
    # use an undefined scope.
    required_scopes = Scopes.validate(scopes.scopes)
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret_key,
            settings.jwt_algorithm,
            issuer=settings.jwt_issuer,
            options={
                "require_jti": True,
                "require_iss": True,
                "require_sub": True,
                "require_iat": True,
                "require_exp": True,
            },
        )
        access_token = OAuth2AccessToken(**claims)
        if Scope.ALL in access_token.scope:
            return access_token
        for scope in required_scopes:
            while scope not in access_token.scope:
                scope, separator, _ = scope.rpartition(":")
                if separator != ":":
                    raise HTTPException(
                        status_code=HTTP_403_FORBIDDEN,
                        error_code="insufficientScope",
                        message="The scopes of the access token are not sufficient for "
                        "this request.",
                        headers={
                            "WWW-Authenticate": 'Bearer error="insufficient_scope", '
                            f'scope="{str(required_scopes)}"'
                        },
                    )
        return access_token
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            error_code="tokenExpired",
            message="The token you used is expired.",
            headers={
                "WWW-Authenticate": 'Bearer error="invalid_token", '
                f'scope="{str(required_scopes)}"'
            },
        )
    except (JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            error_code="invalidToken",
            message="The token you provided is invalid.",
            headers={
                "WWW-Authenticate": 'Bearer error="invalid_token", '
                f'scope="{str(required_scopes)}"'
            },
        )


async def get_user(
    scopes: SecurityScopes,
    token: OAuth2AccessToken = Depends(get_access_token),
) -> Optional[User]:
    domain, separator, user_id = token.subject.partition(":")
    if separator != ":" or domain != "user":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            error_code="invalidToken",
            message="The token you provided is invalid.",
            headers={
                "WWW-Authenticate": 'Bearer error="invalid_token" '
                f'scope="{scopes.scope_str}"'
            },
        )
    try:
        return await User.objects.get(id=user_id)
    except NoMatch:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            error_code="invalidUser",
            message="The access token identifies an unknown user.",
            headers={
                "WWW-Authenticate": 'Bearer error="invalid_token" '
                f'scope="{scopes.scope_str}"'
            },
        )
