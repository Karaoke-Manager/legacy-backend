import uuid
from datetime import datetime
from enum import Enum
from functools import lru_cache
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generator,
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
from passlib.context import CryptContext
from pydantic import BaseModel, Extra, Field, ValidationError, validator
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from karman import db
from karman.exceptions import HTTPException
from karman.models import User
from karman.settings import Settings

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, DictStrAny, MappingIntStrAny

BearerToken: TypeAlias = str
OAuth2ClientID: TypeAlias = str


class Scope(str, Enum):
    """The ``Scope`` enum defines valid scopes that can be used by the Karman API."""

    @classmethod
    @lru_cache
    def all(cls) -> Dict[str, str]:
        """Returns a dictionary mapping scopes to their descriptions."""
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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self._name_}"

    ALL = ("all", "Includes all other scopes. Use with caution.")
    SONGS = ("songs", "Allow full access to songs.")
    READ_SONGS = ("songs:read", "Allow read access to songs.")
    # TODO: Add more scopes


class Scopes(Set[Scope]):
    """
    The ``Scopes`` class represents a set of scopes.

    This class can be used as a Pydantic model field. It implements input validation for
    valid scopes. Note that this class encodes as a **string** and not as a list as one
    might expect. The reason for this behavior is that the OAuth spec defines a scope as
    a space separated string containing the individual scopes. This class can be used to
    be compliant with the spec.

    In order to successfully use this class you must make sure that your models define
    a custom ``json_encoder`` for this class. You can use the ``serialize`` method for
    that purpose or the ``str`` function.
    """

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[Any], "Scopes"], None, None]:
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: "DictStrAny") -> None:
        # A ``Scopes`` instance encodes itself as a string.
        field_schema.clear()
        field_schema["type"] = "string"

    # TODO: Use 'Self' annotation instead in Python 3.11
    @classmethod
    def validate(cls, value: Any) -> "Scopes":
        """
        Implements Pydantic validation. The following input types are recognized:
        - A single string is interpreted as a space separated list of scopes.
        - A list of strings is interpreted as a list of space separated scopes.
        :param value:  The value to be parsed.
        :return: A ``Scopes`` instance.
        :raises ValueError: If the input does not encode a valid ``Scopes`` instance.
        """
        if value == "":
            return cls()
        elif isinstance(value, str):
            return cls(Scope(v) for v in value.split(" "))
        elif isinstance(value, Iterable):
            return cls(Scope(v) for s in value for v in s.split(" "))
        raise TypeError("string required")

    def __str__(self) -> str:
        return self.serialize()

    def serialize(self) -> str:
        """
        Converts a ``Scopes`` instance to its space separated string representation.
        """
        return " ".join(self)


class OAuth2AccessToken(BaseModel):
    """
    This class represents the claims encoded in an OAuth 2.0 access token. It can be
    used to encode and decode claims from a token.
    """

    id: uuid.UUID = Field(..., alias="jti", description="A unique ID for this token.")
    issuer: str = Field(
        default_factory=lambda: Settings.instance().jwt_issuer,
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
    def __validate_expiration(
        cls, v: datetime, values: "DictStrAny", **kwargs: Any
    ) -> datetime:
        if v is not None:
            return v
        if "issued_at" in values:
            issued_at = values["issued_at"]
            return issued_at + Settings.instance().jwt_validity_period
        raise ValueError("issued_at or valid_until must be specified.")

    def dict(
        self,
        *,
        include: Union["AbstractSetIntStr", "MappingIntStrAny", None] = None,
        exclude: Union["AbstractSetIntStr", "MappingIntStrAny", None] = None,
        by_alias: bool = False,
        skip_defaults: Optional[bool] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        encode: bool = False,
    ) -> "DictStrAny":
        """
        Converts the instance to a dict. Parameters behave equivalent to Pydantics
        implementation.

        If you want to encode this instance in a JWT, you should set ``encode`` to true.
        This makes sure that the correct datatypes for JWTs are used.
        """
        data = super().dict(
            include=include,  # type: ignore
            exclude=exclude,  # type: ignore
            by_alias=by_alias or encode,
            skip_defaults=skip_defaults,  # type: ignore
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
        if encode:
            data["jti"] = str(self.id)
            data["scope"] = str(self.scope)
        return data

    class Config:
        extra = Extra.ignore
        # Validate field defaults to set the expiration date
        validate_all = True
        allow_population_by_field_name = True
        # Include the custom encoder here until this issue is solved:
        # https://github.com/samuelcolvin/pydantic/issues/951
        json_encoders = {Scopes: str}


token_url = "token"
authorize_url = "authorize"


class OAuth2Bearer(OAuth2):
    """
    This is the FastAPI security Scheme of Karman. It defines the appropriate OAuth
    OpenAPI documentation.
    """

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
def get_crypt_context() -> CryptContext:
    """Returns the password `CryptContext` used to hash passwords."""
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Generates a hash for the specified ``password``.
    :param password: The password to be hashed.
    :return: The hashed password.
    """
    context = get_crypt_context()
    return str(context.hash(password))


def verify_password(password: str, pw_hash: str) -> bool:
    """
    Verifies whether a given ``password`` matches a hash value.
    :param password: The password to be tested.
    :param pw_hash: The hash value to test the password against.
    :return: Either ``True`` or ``False`` indicating whether the password did match the
             hash.
    """
    context = get_crypt_context()
    return bool(context.verify(password, pw_hash))


def create_access_token(
    user: User, client_id: OAuth2ClientID, scope: Scopes
) -> Tuple[BearerToken, OAuth2AccessToken]:
    """
    Create an access token for the specified ``user``.

    :param user: The user for which to create an access token.
    :param client_id: The ID of the client acting on the user's behalf.
    :param scope: The scope for this token.
    :return: A tuple containing the actual encoded token as well as the claims within
             that token.
    """
    settings = Settings.instance()
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
        settings = Settings.instance()
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
                "require_client_id": True,
                "require_scope": True,
            },
        )
        access_token = OAuth2AccessToken(**claims)
        if Scope.ALL in access_token.scope:
            return access_token
        scope: str
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
    except (JWTError, ValidationError):
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
    session: AsyncSession = Depends(db.session),
) -> Optional[User]:
    """
    Returns the ``User`` associated with the current request.
    :param scopes: The scope required for the requested path operation.
    :param token: The access token provided with the request.
    :param session: A database session.
    :return: The ``User`` associated with the request.
    :raises HTTPException: If no user is associated with the token.
    """
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
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            error_code="invalidUser",
            message="The access token identifies an unknown user.",
            headers={
                "WWW-Authenticate": 'Bearer error="invalid_token" '
                f'scope="{scopes.scope_str}"'
            },
        )
    return user
