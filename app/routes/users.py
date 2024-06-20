from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.database.db import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/")
async def read_users_me():
    # TODO
    return None


@router.patch("/avatar")
async def update_avatar_user(
    file: UploadFile = File(),
    db: Session = Depends(get_db),
):
    # TODO
    return None
