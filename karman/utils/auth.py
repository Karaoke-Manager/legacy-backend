from typing import Collection

import jwt
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt import PyJWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from karman import models
from karman.models import User
from karman.scopes import all_scopes
from .database import database

__all__ = ["create_access_token", "current_user", "admin_user", "required_scopes"]

from ..helpers.crypto import create_jwt_token, TokenPayload, verify_jwt_token


def create_access_token(user: models.User, scopes: Collection[str]) -> jwt.PyJWT:
    if not scopes:
        scopes = user.all_scopes
    for scope in scopes:
        if scope not in user.all_scopes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User does not have the requested scopes."
            )

    encoded_jwt = create_jwt_token(TokenPayload(username=user.username, scopes=scopes or list(user.all_scopes)))
    return encoded_jwt


# TODO: Include Application Root
oauth2_token = OAuth2PasswordBearer(tokenUrl="/v1/login", scopes=all_scopes)


def current_user(security_scopes: SecurityScopes, db: Session = Depends(database),
                 token: str = Depends(oauth2_token)) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    try:
        payload = verify_jwt_token(token)
        user = db.query(User).filter(User.username == payload.username).first()
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


def admin_user(user: User = Depends(current_user)):
    if user.is_admin:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Must be admin",
    )


def required_scopes(*scopes: str):
    def dependency(user: User = Security(current_user, scopes=scopes)):
        return user

    return dependency
