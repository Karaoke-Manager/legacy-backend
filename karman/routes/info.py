from fastapi import APIRouter

from karman import schemas
from karman.config import app_config

router = APIRouter()


@router.get("/",
            response_model=schemas.Info)
async def get_info():
    upload_servers = [{"type": server.server_type, "url": server.url}
                      for server in app_config.upload_servers]
    return {"upload_servers": upload_servers}
