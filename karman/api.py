from fastapi import APIRouter

from karman.resources import auth, user

v1 = APIRouter()
v1.include_router(auth.router, tags=["authentication"])
v1.include_router(user.router, prefix="/users", tags=["users"])
