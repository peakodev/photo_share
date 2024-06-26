from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Comment
from app.schemas.comments import CommentCreate, CommentUpdate


async def get_comment_by_id(comment_id: int, db: Session) -> Comment | None:
    query = select(Comment).filter_by(id=comment_id)
    comment = db.execute(query)
    return comment.scalar_one_or_none()


async def get_comments_by_post(
    post_id: int, offset: int, limit: int, db: Session
) -> List[Comment] | None:
    query = (
        select(Comment)
        .filter_by(post_id=post_id)
        .group_by(Comment.created_at, Comment.id)
        .offset(offset)
        .limit(limit)
    )
    comments = db.execute(query)
    return comments.scalars().all()


async def create_comment(
    comment: CommentCreate, user_id: int, db: Session
) -> Comment:
    db_comment = Comment(**comment.model_dump(exclude_unset=True), user_id=user_id)
    print(db_comment.post_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


async def update_comment(
    comment_id: int, comment: CommentUpdate, db: Session
) -> Comment:
    db_comment = db.query(Comment).filter_by(id=comment_id).first()
    for key, value in comment.model_dump(exclude_unset=True).items():
        setattr(db_comment, key, value)
    db.commit()
    db.refresh(db_comment)
    return db_comment


async def delete_comment(comment_id: int, db: Session) -> Comment:
    comment = db.query(Comment).filter_by(id=comment_id).first()
    db.delete(comment)
    db.commit()
    return comment
