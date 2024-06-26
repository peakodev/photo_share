from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, UploadFile, status
from sqlalchemy.orm import Session

from app.models import get_db
from app.models.post import Post
from app.schemas.post import PostDeleteSchema, PostResponse
from app.services.role_checker import admin_required
from app.repository.admin import delete_post_by_id, update_post_by_id

router = APIRouter(prefix="/admin", tags=["admin"])

@router.delete("/delete_post/{post_id}",
                response_model=PostDeleteSchema,
                dependencies=[Depends(admin_required)])
async def admin_delete_post_by_id(post_id: int, db: Session = Depends(get_db)) -> Post | None:
    """
    Deletes a post by id, the function works only for users with administrator rights.
    Args:
        post_id (int): id of post to delete.
        db (Session, optional): The database session.
    Raises:
        HTTPException: HTTP_403_FORBIDDEN
        HTTPException: HTTP_404_NOT_FOUND
    
    Returns:
        Post | None: Database model Post or None
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
                                  created_at: datetime = None,
                                  updated_at: datetime = None,
                                  tags: str = None,
                                  rating: float = None
                                                        ) -> Post | None:
    """
    Update a post by id, the function works only for users with administrator rights.

    Args:
        post_id (int): id of post to update.
        db (Session): The database session.
        photo (UploadFile, optional): New photo for post.
        description (str, optional): New description for post.
        created_at (datetime, optional): Format yyyy-mm-dd hh:mm:ss.mss
        updated_at (datetime, optional): Format yyyy-mm-dd hh:mm:ss.mss
        tags (str, optional): New tags for post
        rating (int, optional): New rating for post

    Raises:
        HTTPException: HTTP_403_FORBIDDEN,
        HTTPException: HTTP_404_NOT_FOUND

    Returns:
        Post | None: Database model Post or None
    """    
    post = await update_post_by_id(post_id,
                                   db,
                                   photo,
                                   description,
                                   created_at,
                                   updated_at,
                                   tags,
                                   rating,
                                   )
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post

