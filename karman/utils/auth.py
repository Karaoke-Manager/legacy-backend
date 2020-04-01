from typing import Collection

import jwt
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt import PyJWTError
from motor.core import AgnosticDatabase
from pydantic import ValidationError

from karman import models
from karman.scopes import all_scopes
from .mongo import get_db
from ..helpers.crypto import create_jwt_token, TokenPayload, verify_jwt_token

__all__ = ["create_access_token", "current_user", "admin_user", "required_scopes"]


def create_access_token(user: models.User, scopes: Collection[str]) -> jwt.PyJWT:
    if not scopes:
        scopes = user.all_scopes
    for scope in scopes:
        if scope not in user.all_scopes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User does not have the requested scopes."
            )

    # TODO: Should this be async?
    encoded_jwt = create_jwt_token(TokenPayload(username=user.username, scopes=scopes or list(user.all_scopes)))
    return encoded_jwt


# TODO: Include Application Root
oauth2_token = OAuth2PasswordBearer(tokenUrl="/v1/login", scopes=all_scopes)


async def current_user(security_scopes: SecurityScopes,
                       db: AgnosticDatabase = Depends(get_db),
                       token: str = Depends(oauth2_token)) -> models.User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    try:
        payload = verify_jwt_token(token)
        user = models.User(**await db.users.find_one({"username": payload.username}))
        for scope in security_scopes.scopes:
            if scope not in payload.scopes and not user.is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions",
                )
        if user is not None:
            return user
    except (PyJWTError, KeyError, ValidationError):
        # Invalid JWT
        pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )


async def admin_user(user: models.User = Depends(current_user)):
    if user.is_admin:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Must be admin",
    )


def required_scopes(*scopes: str):
    async def dependency(user: models.User = Security(current_user, scopes=scopes)):
        return user

    return dependency
