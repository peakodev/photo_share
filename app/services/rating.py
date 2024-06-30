from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.post import Post
from app.models.user import User
from app.models.rating import Rating

async def add_rate_to_post(user: User,
                           post: Post,
                           rating: int,
                           db: Session) -> int:
    
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
    average_rate_query = db.query(func.avg(Rating.rate).label('average_rate')).filter(Rating.post_id == post.id).first()
    average_rate = average_rate_query.average_rate
    post.rating = float(round(average_rate, 2))
    db.add(post)
    db.commit()
    db.refresh(post)
    return post.rating
     