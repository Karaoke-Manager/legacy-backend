from fastapi import APIRouter, Depends

from karman.routes import auth, users, roles, imports, info
from karman.scopes import MANAGE_USERS, IMPORT_SONGS
from karman.utils import required_scopes

__all__ = ["v1"]

v1 = APIRouter()
v1.include_router(info.router,
                  prefix="/info",
                  tags=["info"])
v1.include_router(auth.router,
                  tags=["authentication"])
v1.include_router(users.router,
                  prefix="/users",
                  tags=["users"])
v1.include_router(roles.router,
                  prefix="/roles",
                  dependencies=[Depends(required_scopes(MANAGE_USERS))],
                  tags=["roles"])

v1.include_router(imports.router,
                  prefix="/imports",
                  dependencies=[Depends(required_scopes(IMPORT_SONGS))],
                  tags=["imports", "songs"])
