from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary
import cloudinary.uploader

from app.database.db import get_db
from app.database.models import User
from app.repository import users as repository_users
from app.services.auth import auth_service
from app.conf.config import settings
from app.schemas.user import UserDb

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Get the current user.

    Args:
        current_user (User, optional): The current user. Defaults to Depends(auth_service.get_current_user).

    Returns:
        _type_: The current user.
    """
    return current_user


@router.patch("/avatar", response_model=UserDb)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the avatar for the current user.

    Args:
        file (UploadFile, optional): The file to upload. Defaults to File().
        current_user (User, optional): The current user. Defaults to Depends(auth_service.get_current_user).
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        _type_: The updated user.
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

    r = cloudinary.uploader.upload(
        file.file, public_id=f"ContactsApp/{current_user.id}", overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(f"ContactsApp/{current_user.id}").build_url(
        width=250, height=250, crop="fill", version=r.get('version')
    )
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
