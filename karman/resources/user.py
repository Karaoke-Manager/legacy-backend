from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from karman import schemas, models
from karman.database import db

router = APIRouter()


@router.get(
    "/",
    response_model=schemas.User
)
def list_users(db: Session = Depends(db)):
    return db.query(models.User).all()
