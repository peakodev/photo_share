from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, UploadFile, status
from sqlalchemy.orm import Session

from app.models import get_db
from app.models.post import Post
from app.schemas.post import PostDeleteSchema, PostResponse
from app.schemas.user import UserDb
from app.services.role_checker import admin_required
from app.repository.admin import delete_post_by_id, update_post_by_id
from app.repository.users import get_user_by_id, ban_user

router = APIRouter(prefix="/admin", tags=["admin"])


@router.delete("/delete_post/{post_id}",
               response_model=PostDeleteSchema,
               dependencies=[Depends(admin_required)])
async def admin_delete_post_by_id(post_id: int, db: Session = Depends(get_db)) -> Post | None:
    """
    Deletes a post by id, the function works only for users with administrator rights.

    Args:
        post_id (int):  Database object Post.id to delete.
        db (Session, optional):  The database session.
    Raises:
        HTTPException:  HTTP_403_FORBIDDEN
        HTTPException:  HTTP_404_NOT_FOUND
    Returns:
        Post | None:  Database model Post or None
    """    
    result = await delete_post_by_id(post_id, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return result


@router.put("/update_post/{post_id}",
            response_model=PostResponse,
            dependencies=[Depends(admin_required)])
async def admin_update_post_by_id(post_id: int,
                                  db: Session = Depends(get_db),
                                  photo: UploadFile = None,
                                  description: str = None,
                                  tags: str = None,
                                  rating: int = None
                                                        ) -> Post | None:
    """
    Update a post by id, the function works only for users with administrator rights.

    Args:
        post_id (int):  Database object Post.id to update.
        db (Session, optional):  The database session.
        photo (UploadFile , optional):  New photo for post.
        description (str, optional):  New description for post.
        tags (str, optional):  New tags for post
        rating (int, optional):  New rating for post.
    Raises:
        HTTPException:  HTTP_403_FORBIDDEN.
        HTTPException:  HTTP_404_NOT_FOUND.
    Returns:
        Post | None:  Database object Post

    """
    post = await update_post_by_id(post_id,
                                   db,
                                   photo,
                                   description,
                                   tags,
                                   rating,
                                   )
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("/ban_user/{user_id}",
             response_model=UserDb,
             dependencies=[Depends(admin_required)])
async def banning_user_by_id(user_id: int, db: Session = Depends(get_db)) -> UserDb:
    """
    Ban a user by id.

    UserDb schema {
                   id: int,
                   first_name: str,
                   last_name: str,
                   email: str,
                   created_at: datetime,
                   avatar: str,
                   role: Role,
                   banned: bool,
                   posts_number: int,
                   comments_number: int
                   }
    
    Args:
        user_id (int):  Id of user to ban.
        db (Session, optional):  The database session.
    Raises:
        HTTPException:  HTTP_404_NOT_FOUND.
        HTTPException:  HTTP_400_BAD_REQUEST.
    Returns:
        UserDb:  Schema

    """    
    user = await get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.banned:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already banned")

    await ban_user(user_id, True, db)

    return user


@router.post("/unban_user/{user_id}",
             response_model=UserDb,
             dependencies=[Depends(admin_required)])
async def unbanning_user_by_id(user_id: int, db: Session = Depends(get_db)) -> UserDb:
    """
    Unban a user by id.

    UserDb schema {
                id: int,
                first_name: str,
                last_name: str,
                email: str,
                created_at: datetime,
                avatar: str,
                role: Role,
                banned: bool,
                posts_number: int,
                comments_number: int,
                }

    Args:
        user_id (int):  id of user to unban.
        db (Session, optional):  The database session.
    Raises:
        HTTPException:  HTTP_404_NOT_FOUND.
        HTTPException:  HTTP_400_BAD_REQUEST.
    Returns:
        UserDb:  Schema

    """    
    user = await get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.banned:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already unbanned")

    await ban_user(user_id, False, db)

    return user
