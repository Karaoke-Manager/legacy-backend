from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import Response

from karman import schemas, models
from karman.models import User
from karman.utils import current_user, database
from karman.utils.upload import UploadManager

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.Import
)
async def create_import(data: schemas.CreateImport,
                        response: Response,
                        user: User = Depends(current_user),
                        db: Session = Depends(database),
                        uploader: UploadManager = Depends()):
    imp = models.Import(name=data.name, user=user)
    db.add(imp)  # FIXME: Async!!
    db.commit()
    uid = await uploader.register_upload(finish_import_upload, imp.id)
    response.headers["Upload-ID"] = str(uid)
    return imp


async def finish_import_upload(file: str, upload_id: int):
    print("File: " + file)
