from fastapi import APIRouter

router = APIRouter()

# @router.get(
#    "/",
#    response_model=schemas.User
# )
# def list_users(db: Session = Depends(database), user: models.User = Depends(current_user)):
#    return db.query(models.User).all()
