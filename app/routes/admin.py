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

    :param post_id: Database object Post.id to delete.
    :type post_id: int
    :param db: The database session.
    :type db: Session, optional
    :raises HTTPException: HTTP_403_FORBIDDEN
    :raises HTTPException: HTTP_404_NOT_FOUND
    :return: Database model Post or None
    :rtype: Post | None
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

    :param post_id: Database object Post.id to update.
    :type post_id: int
    :param db: The database session.
    :type db: Session, optional
    :param photo: New photo for post.
    :type photo: UploadFile , optional
    :param description: New description for post.
    :type description: str, optional
    :param tags: New tags for post
    :type tags: str, optional
    :param rating: New rating for post.
    :type rating: int, optional
    :raises HTTPException: HTTP_403_FORBIDDEN
    :raises HTTPException: HTTP_404_NOT_FOUND
    :return: Database object Post
    :rtype: Post | None
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
                   id: int\n
                   first_name: str\n
                   last_name: str\n
                   email: str\n
                   created_at: datetime\n
                   avatar: str\n
                   role: Role\n
                   banned: bool\n
                   posts_number: int\n
                   comments_number: int\n
                   }
    
    :param user_id: Id of user to ban.
    :type user_id: int
    :param db: The database session.
    :type db: Session, optional
    :raises HTTPException: HTTP_404_NOT_FOUND
    :raises HTTPException: HTTP_400_BAD_REQUEST
    :return: Schema
    :rtype: UserDb
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
                id: int\n
                first_name: str\n
                last_name: str\n
                email: str\n
                created_at: datetime\n
                avatar: str\n
                role: Role\n
                banned: bool\n
                posts_number: int\n
                comments_number: int\n
                }

    :param user_id: id of user to unban.
    :type user_id: int
    :param db: The database session.
    :type db: Session, optional
    :raises HTTPException: HTTP_404_NOT_FOUND
    :raises HTTPException: HTTP_400_BAD_REQUEST
    :return: Schema
    :rtype: UserDb
    """    
    user = await get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.banned:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already unbanned")

    await ban_user(user_id, False, db)

    return user
