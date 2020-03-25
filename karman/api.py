from fastapi import APIRouter

from karman.resources import user

v1 = APIRouter()
v1.include_router(user.router, prefix="/users", tags=["users"])
