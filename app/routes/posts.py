from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Depends,
    UploadFile,
    status,
    Query,
)

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import User, Role, get_db, Rating, Post
from app.schemas.post import (
    PostResponse,
    PostCreateResponse,
    PostDeleteSchema,
    PostSearchSchema
)
from app.repository import posts as repository_posts
from app.repository import users as repository_users
from app.services.auth import auth_service
from app.services.cloudinary import Effect
from app.services.rating import add_rate_to_post
from app.schemas.post import RatingResponce

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get(
    "/",
    response_model=list[PostResponse] | None,
    name="get_posts",
)
async def get_posts(
    limit: int = Query(10),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    return await repository_posts.get_posts(limit, offset, user, db)


@router.get(
    "/all",
    response_model=list[PostResponse],
    name="get_all_posts",
)
async def get_all_posts(
    limit: int = Query(10),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):

    posts = await repository_posts.get_all_posts(limit, offset, db)
    return posts


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    name="get_post_by_id",
)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    post = await repository_posts.get_post_by_id(post_id, db)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@router.post(
    "/search",
    name="search_posts_by_query",
    response_model=list[PostResponse],
)
async def search_posts(
    search_schema: PostSearchSchema,
    db: Session = Depends(get_db)
):
    return await repository_posts.search_posts_by_inputs(search_schema, db)


@router.post(
    "/create",
    name="create_post",
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
            detail=f"You can't create this post for user {user_email}",
        )
    if user_email and user.role == Role.admin:
        user = await repository_users.get_user_by_email(user_email, db)
    new_post = await repository_posts.create_post(description, tags, file, user, db)
    return new_post


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    name="update_post",
)
async def update_post(
    post_id: int,
    description: str = None,
    tags: str = None,
    effect: Effect = None,
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
            detail=f"You can't update  post for user {post.user.email}",
        )

    return post


@router.delete(
    "/{post_id}",
    name="delete_post",
    response_model=PostDeleteSchema,
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
            detail="Insufficient permissions to delete this post",
        )

    return post

@router.post('/rate/{post_id}',response_model=RatingResponce)
async def rate_post(post_id: int, rating: int, db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    The user rates the post from 1 to 5.
    Calculates the average rating from all ratings for this post.
    The rating of the post is updated in database object Post.rating

    Args:
        post_id (int): id of post to rate.
        rating (int): Score from 1 to 5
        db (Session, optional): The database session
        user (User, optional): The user to rate post

    Raises:
        HTTPException: HTTP_403_FORBIDDEN - User not authorizated.
        HTTPException: HTTP_406_NOT_ACCEPTABLE - Rating values in range 1-5.
        HTTPException: HTTP_404_NOT_FOUND - Post not found.
        HTTPException: HTTP_409_CONFLICT - Owner can't rate his post.
        HTTPException: HTTP_409_CONFLICT - Post already rated.

    Returns:
        _type_: _description_
    """    
    if rating not in range(1,6):
           raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Rating values in range 1-5")
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.user == user:
          raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Owner can't rate his post")
    if db.query(Rating).filter(Rating.post == post, Rating.user == user).first():
          raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Post already rated")
    result = await add_rate_to_post(user=user, post=post, rating=rating, db=db)
    return result

