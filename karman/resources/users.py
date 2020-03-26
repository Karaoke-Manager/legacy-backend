from typing import List

from fastapi import APIRouter, Depends

from karman import schemas, models
from karman.database import Session, database
from karman.scopes import MANAGE_USERS
from karman.utils import required_scopes

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(required_scopes(MANAGE_USERS))],
    response_model=List[schemas.User]
)
def list_users(db: Session = Depends(database)):
    return db.query(models.User).all()
