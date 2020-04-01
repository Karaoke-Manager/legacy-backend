from typing import List

from bson import ObjectId
from fastapi import APIRouter, Depends
from motor.core import AgnosticDatabase
from starlette import status

from karman import schemas, models
from karman.utils import get_db

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
async def add_role(data: schemas.CreateRole, db: AgnosticDatabase = Depends(get_db)):
    # FIXME: Handle Integrity Errors
    role = models.Role(**data.dict())
    role_id = await db.roles.insert_one(role.json())
    role.id = role_id
    return role


@router.get(
    "/",
    response_model=List[schemas.Role]
)
async def list_roles(db: AgnosticDatabase = Depends(get_db)):
    return await db.roles.find()


@router.get(
    "/{role_id}",
    response_model=schemas.Role
)
async def get_role(role_id: ObjectId, db: AgnosticDatabase = Depends(get_db)):
    # return get_or_404(db, models.Role, role_id)
    # FIXME: Handle 404
    return await db.roles.find_one({"_id": role_id})


@router.put(
    '/{role_id}',
    response_model=schemas.Role
)
def update_role(role_id: int, data: schemas.UpdateRole, db: AgnosticDatabase = Depends(get_db)):
    # TODO: Implement
    pass
    # try:
    #     role: models.Role = get_or_404(db, models.Role, role_id)
    #     if data.id and role_id != data.id:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="IDs cannot be changed")
    #     role.name = data.name
    #     role.scopes = data.scopes
    #     db.commit()
    #     return role
    # except IntegrityError:
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Role {data.name} does already exist.")


@router.patch(
    "/{role_id}",
    response_model=schemas.Role
)
def patch_role(role_id: int, data: schemas.PatchRole, db: AgnosticDatabase = Depends(get_db)):
    pass
    # TODO: Implement
    # try:
    #     role: models.Role = get_or_404(db, models.Role, role_id)
    #     if data.id and role_id != data.id:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="IDs cannot be changed")
    #     if data.name:
    #         role.name = data.name
    #     if data.scopes:
    #         role.scopes = data.scopes
    #     db.commit()
    #     return role
    # except IntegrityError:
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Role {data.name} does already exist.")


@router.delete(
    "/{role_id}",
    response_model=schemas.Role
)
async def delete_role(role_id: ObjectId, db: AgnosticDatabase = Depends(get_db)):
    return await db.roles.find_one_and_delete({"_id": role_id})
