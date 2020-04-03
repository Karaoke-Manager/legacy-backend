from typing import List

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from karman import schemas, models
from karman.scopes import MANAGE_USERS
from karman.utils import required_scopes, get_db

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(required_scopes(MANAGE_USERS))],
    response_model=List[schemas.User]
)
async def list_users(db: AsyncIOMotorDatabase = Depends(get_db)):
    # TODO: Pagination?
    return [user async for user in models.User.all(db)]
