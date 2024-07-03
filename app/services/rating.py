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

    Args:
        user (User):  Appraiser.
        post (Post):  Database object Post to rate.
        rating (int):  1-5.
        db (Session):  The database session.
    Returns:
        dict:  {"post_id": int, "rating": float}
    """    
    
    result = Rating(post_id=post.id,
                    user_id=user.id,
                    rate=rating,
                    create_at=datetime.now())
    db.add(result)
    db.commit()
    db.refresh(result)
    rating = await calculate_avarage_rating(post, db)
    return {"post_id": post.id, "rating": rating}


async def calculate_avarage_rating(post: Post, db: Session):
    """
    Calculate avarage rating for Post

    Args:
        post (Post):  Database object Post to calculate.
        db (Session):  The database session.
    Returns:
        float:  Post.rating
    """    
    average_rate_query = db.query(func.avg(Rating.rate).label('average_rate')).filter(Rating.post_id == post.id).first()
    average_rate = average_rate_query.average_rate
    post.rating = float(round(average_rate, 2))
    db.add(post)
    db.commit()
    db.refresh(post)
    return post.rating
     