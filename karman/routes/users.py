from typing import List

from fastapi import APIRouter, Depends
from motor.core import AgnosticDatabase

from karman import schemas
from karman.scopes import MANAGE_USERS
from karman.utils import required_scopes, get_db

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(required_scopes(MANAGE_USERS))],
    response_model=List[schemas.User]
)
async def list_users(db: AgnosticDatabase = Depends(get_db)):
    return await db.users.find()
