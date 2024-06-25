from fastapi import APIRouter, File, HTTPException, Depends, UploadFile, status, Query

from sqlalchemy.orm import Session

from app.models import User, Role, get_db
from app.schemas.post import (
    PostResponse,
    PostCreateResponse,
    PostDeleteSchema,
)
from app.repository import posts as repository_posts
from app.repository import users as repository_users
from app.services.auth import auth_service

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get(
    "/",
    response_model=list[PostResponse],
)
async def get_posts(
    limit: int = Query(10),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    posts = await repository_posts.get_posts(limit, offset, user, db)
    return posts


@router.get(
    "/all",
    response_model=list[PostResponse],
)
async def get_all_posts(
    limit: int = Query(10),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    # user: User = Depends(auth_service.get_current_user),
):

    posts = await repository_posts.get_all_posts(limit, offset, db)
    return posts


@router.get(
    "/{post_id}",
    response_model=PostResponse,
)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    post = await repository_posts.get_post(post_id, user, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@router.get(
    "/find/",
    response_model=list[PostResponse],
)
async def find_post(
    find_str: str,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):

    posts = await repository_posts.find_posts(find_str, user, db)
    if len(posts) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=" Post not found"
        )
    return posts


@router.post(
    "/create",
    response_model=PostCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    description: str,
    tags: str = None,
    user_email: str = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
 
    if user_email and user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You can't create this post for user {user_email}"
        )
    if user_email and user.role == Role.admin:
        user = await repository_users.get_user_by_email(user_email, db)
    new_post = await repository_posts.create_post(description, tags, file, user, db)
    return new_post


@router.put(
    "/{post_id}",
    response_model=PostResponse,
)
async def update_post(
    post_id: int,
    description: str = None,
    tags: str = None,
    effect: str = None,
    # user_email: str = None,
    file: UploadFile = File(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    post = await repository_posts.get_post_by_id(post_id, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if user.role == Role.admin:
        post = await repository_posts.update_post(
            post_id, post.user, db, description, tags, effect, file
        )
    elif user.id == post.user.id:
        post = await repository_posts.update_post(
            post_id, user, db, description, tags, effect, file
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You can't update  post for user {post.user.email}"
        )
    
    return post


@router.delete(
    "/{post_id}",
    response_model=PostDeleteSchema
)
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    post = await repository_posts.get_post_by_id(post_id, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if post.user_id == user.id or user.role == Role.admin:
        post = await repository_posts.delete_post(post_id, user, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete this post"
        )

    return post
