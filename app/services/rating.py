from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.post import Post
from app.models.user import User
from app.models.rating import Rating

async def add_rate_to_post(user: User,
                           post: Post,
                           rating: int,
                           db: Session) -> dict:
    """
    Add rate to post

    :param user: Appraiser
    :type user: User
    :param post: Database object Post to rate.
    :type post: Post
    :param rating: 1-5
    :type rating: int
    :param db: The database session.
    :type db: Session
    :return: {"post_id": int, "rating": float}
    :rtype: dict
    """    
    
    result = Rating(post_id = post.id,
                    user_id = user.id,
                    rate = rating,
                    create_at = datetime.now())
    db.add(result)
    db.commit()
    db.refresh(result)
    rating = await calculate_avarage_rating(post, db)
    return {"post_id": post.id, "rating": rating}

async def calculate_avarage_rating(post: Post, db: Session):
    """
    Calculate avarage rating for Post

    :param post: Database object Post to calculate
    :type post: Post
    :param db: The database session.
    :type db: Session
    :return: Post.rating
    :rtype: float
    """    
    average_rate_query = db.query(func.avg(Rating.rate).label('average_rate')).filter(Rating.post_id == post.id).first()
    average_rate = average_rate_query.average_rate
    post.rating = float(round(average_rate, 2))
    db.add(post)
    db.commit()
    db.refresh(post)
    return post.rating
     