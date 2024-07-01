from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Comment
from app.schemas.comments import CommentCreate, CommentUpdate


async def get_comment_by_id(comment_id: int, db: Session) -> Comment | None:
    """
    Get comment by id.

    :param comment_id: Database object Comment.id to search.
    :type comment_id: int
    :param db: The database session.
    :type db: Session
    :return: Database object Comment.
    :rtype: Comment | None
    """    
    query = select(Comment).filter_by(id=comment_id)
    comment = db.execute(query)
    return comment.scalar_one_or_none()


async def get_comments_by_post(
    post_id: int, offset: int, limit: int, db: Session
) -> List[Comment] | None:
    """
    Get comments by post id.

    Return all comments for post.

    :param post_id: Database object Post.id to search.
    :type post_id: int
    :param offset: Offset.
    :type offset: int
    :param limit: Limit.
    :type limit: int
    :param db: The database session.
    :type db: Session
    :return: Commets for post.
    :rtype: List[Comment] | None
    """    
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
    """
    Create comment.

    CommentCreate schema (post_id: int\n
                          text: str)

    :param comment: Schema.
    :type comment: CommentCreate
    :param user_id: Owner id.
    :type user_id: int
    :param db: The database session.
    :type db: Session
    :return: Database object Comment.
    :rtype: Comment
    """    
    db_comment = Comment(**comment.model_dump(exclude_unset=True), user_id=user_id)
    print(db_comment.post_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


async def update_comment(
    comment_id: int, comment: CommentUpdate, db: Session
) -> Comment:
    """
    Update comment 

    CommentUpdate schema (text: Optional[str] = None)

    :param comment_id: Database object Comment.id to update.
    :type comment_id: int
    :param comment: Schema.
    :type comment: CommentUpdate
    :param db: The database session.
    :type db: Session
    :return: Database object Comment.
    :rtype: Comment
    """    
    db_comment = db.query(Comment).filter_by(id=comment_id).first()
    for key, value in comment.model_dump(exclude_unset=True).items():
        setattr(db_comment, key, value)
    db.commit()
    db.refresh(db_comment)
    return db_comment


async def delete_comment(comment_id: int, db: Session) -> Comment:
    """
    Delete comment

    :param comment_id: Database object Comment.id to delete.
    :type comment_id: int
    :param db: The database session.
    :type db: Session
    :return: Database object Comment.
    :rtype: Comment
    """    
    comment = db.query(Comment).filter_by(id=comment_id).first()
    db.delete(comment)
    db.commit()
    return comment
