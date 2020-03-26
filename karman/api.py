from fastapi import APIRouter, Depends

from karman.resources import auth, users, roles
from karman.scopes import MANAGE_USERS
from karman.utils import required_scopes

v1 = APIRouter()
v1.include_router(auth.router, tags=["authentication"])
v1.include_router(users.router, prefix="/users", tags=["users"])
v1.include_router(roles.router,
                  prefix="/roles",
                  dependencies=[Depends(required_scopes(MANAGE_USERS))],
                  tags=["roles"])
