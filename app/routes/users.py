from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from typing import Optional

from app.models import User, get_db
from app.repository import users as repository_users
from app.services.auth import auth_service
from app.services.cloudinary import upload_avatar
from app.conf.config import settings
from app.schemas.user import UserDb, UserUpdateModel

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{current_user_id}/", response_model=UserDb)
async def get_user_info(
    user_id: Optional[int] = None,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    if user_id != current_user.id and user_id:
        current_user = await repository_users.get_user_by_id(user_id, db)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=" User not found"
        )
    posts_number, comments_number = await repository_users.user_posts_comments_number(
        current_user, db
    )
    current_user.posts_number = posts_number
    current_user.comments_number = comments_number
    return current_user


@router.put("/{current_user_id}/", response_model=UserDb)
async def update_user_info(
    first_name: str = None,
    last_name: str = None,
    email: str = None,
    avatar: UploadFile = File(default=None),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    if avatar:
        avatar = await upload_avatar(avatar, current_user)

    body = UserUpdateModel(
        first_name=first_name, 
        last_name=last_name, 
        email=email,
        avatar=avatar
    )
    updated_user = await repository_users.update_user(current_user.id, body, db)
    return updated_user

