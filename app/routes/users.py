from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.models import User, get_db
from app.repository import users as repository_users
from app.services.auth import auth_service
from app.services.cloudinary import upload_avatar
from app.schemas.user import UserDb, UserUpdateModel, PublicUserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UserDb, name="get_user")
async def get_me(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):

    """
    Me

    Args:
        current_user (User, optional):  Current user.
        db (Session, optional):  The database session.
    Raises:
        HTTPException:  HTTP_404_NOT_FOUND
    Returns:
        User:  Database object User.
    """    

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    posts_number, comments_number = await repository_users.user_posts_comments_number(
        current_user, db
    )
    current_user.posts_number = posts_number
    current_user.comments_number = comments_number
    return current_user


@router.get("/{user_id}/", response_model=UserDb, name="get_user_by_id")
async def get_user_info(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    User info

    Args:
        user_id (Optional[int], optional):  Database object User.id to search.
        db (Session, optional):  The database session.
    Raises:
        HTTPException:  HTTP_404_NOT_FOUND.
    Returns:
        User:  Database object User.
    """    
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    posts_number, comments_number = await repository_users.user_posts_comments_number(
        user, db
    )
    user.posts_number = posts_number
    user.comments_number = comments_number
    return user


@router.put("/", response_model=UserDb, name="update_user")
async def update_user_info(
    first_name: str = None,
    last_name: str = None,
    email: str = None,
    avatar: UploadFile = File(default=None),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update user info.

    Parameters are optional.

    Args:
        first_name (str, optional):  New first name for user.
        last_name (str, optional):  New last name for user.
        email (str, optional):  New email for user.
        avatar (UploadFile, optional):  New avatar for user.
        current_user (User, optional):  Current user
        db (Session, optional):  The database session.
    Returns:
        User:  Database object User.
    """    
    if avatar:
        avatar = await upload_avatar(avatar, current_user)

    body = UserUpdateModel(
        id=current_user.id, first_name=first_name, last_name=last_name, email=email, avatar=avatar
    )
    updated_user = await repository_users.update_user(current_user.id, body, db)
    return updated_user
