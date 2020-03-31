from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from karman import schemas, models
from karman.utils import get_or_404, database

router = APIRouter()


@router.post(
    '/',
    response_model=schemas.Role,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": schemas.HttpError,
            "description": "If a role with the specified name already exists."
        }
    }
)
def add_role(data: schemas.CreateRole, db: Session = Depends(database)):
    try:
        role = models.Role(name=data.name, scopes=data.scopes)
        db.add(role)
        db.commit()
        return role
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Role {data.name} does already exist.")


@router.get(
    "/",
    response_model=List[schemas.Role]
)
def list_roles(db: Session = Depends(database)):
    return db.query(models.Role).all()


@router.get(
    "/{role_id}",
    response_model=schemas.Role
)
def get_role(role_id: int, db: Session = Depends(database)):
    return get_or_404(db, models.Role, role_id)


@router.put(
    '/{role_id}',
    response_model=schemas.Role
)
def update_role(role_id: int, data: schemas.UpdateRole, db: Session = Depends(database)):
    try:
        role: models.Role = get_or_404(db, models.Role, role_id)
        if data.id and role_id != data.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="IDs cannot be changed")
        role.name = data.name
        role.scopes = data.scopes
        db.commit()
        return role
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Role {data.name} does already exist.")


@router.patch(
    "/{role_id}",
    response_model=schemas.Role
)
def patch_role(role_id: int, data: schemas.PatchRole, db: Session = Depends(database)):
    try:
        role: models.Role = get_or_404(db, models.Role, role_id)
        if data.id and role_id != data.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="IDs cannot be changed")
        if data.name:
            role.name = data.name
        if data.scopes:
            role.scopes = data.scopes
        db.commit()
        return role
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Role {data.name} does already exist.")


@router.delete(
    "/{role_id}",
    response_model=schemas.Role
)
def delete_role(role_id: int, db: Session = Depends(database)):
    role: models.Role = get_or_404(db, models.Role, role_id)
    db.delete(role)
    db.commit()
    return role
