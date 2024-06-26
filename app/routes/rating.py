from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import Rating, User, Post, get_db
from app.services.auth import auth_service
from app.repository.posts import get_post
from app.repository.ratings import add_rate_to_post
from app.schemas.post import PostResponse

router = APIRouter(prefix="/rating", tags=["rating"])

@router.post('/{post_id}',response_model=PostResponse)
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

