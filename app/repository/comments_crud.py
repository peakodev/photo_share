from sqlalchemy.orm import Session
from app.database.comment import Comment
from app.schemas.comments import CommentCreate, CommentUpdate


def get_comment(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()


def get_comments_by_post(db: Session, post_id: int, skip: int = 0, limit: int = 10):
    return db.query(Comment).filter(Comment.post_id == post_id).offset(skip).limit(limit).all()


def create_comment(db: Session, comment: CommentCreate, user_id: int, post_id: int):
    db_comment = Comment(**comment.dict(), user_id=user_id, post_id=post_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def update_comment(db: Session, comment_id: int, comment: CommentUpdate):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment:
        for key, value in comment.dict(exclude_unset=True).items():
            setattr(db_comment, key, value)
        db.commit()
        db.refresh(db_comment)
    return db_comment


def delete_comment(db: Session, comment_id: int):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        return None
    db.delete(db_comment)
    db.commit()
    return db_comment