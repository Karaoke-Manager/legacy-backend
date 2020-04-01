from bson import ObjectId
from fastapi import APIRouter, Depends
from motor.core import AgnosticDatabase
from starlette.responses import Response

from karman import schemas, models
from karman.models import User
from karman.utils import current_user, get_db
from karman.utils.upload import UploadManager

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.Import
)
async def create_import(data: schemas.CreateImport,
                        response: Response,
                        user: User = Depends(current_user),
                        db: AgnosticDatabase = Depends(get_db),
                        uploader: UploadManager = Depends()):
    imp = models.Import(name=data.name, user=user)
    await db.imports.insert_one(imp.json())
    uid = await uploader.register_upload(finish_import_upload, imp.id)
    response.headers["Upload-ID"] = str(uid)
    return imp


async def finish_import_upload(file: str, upload_id: ObjectId):
    print("File: " + file)
