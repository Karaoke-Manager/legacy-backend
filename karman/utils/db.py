from typing import Type, Any

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from karman.models import Model


def get_or_404(db: Session, cls: Type[Model], value: Any):
    object = db.query(cls).get(value)
    if not object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return object
