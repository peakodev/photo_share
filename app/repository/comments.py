from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Comment
from app.schemas.comments import CommentCreate, CommentUpdate


async def get_comment_by_id(comment_id: int, db: AsyncSession) -> Comment | None:
    query = select(Comment).filter_by(id=comment_id)
    comment = await db.execute(query)
    return comment.scalar_one_or_none()


async def get_comments_by_post(
    post_id: int, offset: int, limit: int, db: AsyncSession
) -> List[Comment] | None:
    query = (
        select(Comment)
        .filter_by(post_id=post_id)
        .group_by(Comment.created_at, Comment.id)
        .offset(offset)
        .limit(limit)
    )
    comments = await db.execute(query)
    return comments.scalars().all()


async def create_comment(
    comment: CommentCreate, user_id: int, db: AsyncSession
) -> Comment:
    db_comment = Comment(**comment.model_dump(exclude_unset=True), user_id=user_id)
    print(db_comment.post_id)
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment


async def update_comment(
    comment_id: int, comment: CommentUpdate, db: AsyncSession
) -> Comment | None:
    query = select(Comment).filter_by(id=comment_id)
    db_comment = await db.execute(query)
    db_comment = db_comment.scalar_one_or_none()
    if db_comment:
        for key, value in comment.model_dump(exclude_unset=True).items():
            setattr(db_comment, key, value)
        await db.commit()
        await db.refresh(db_comment)
    return db_comment


async def delete_comment(comment_id: int, db: AsyncSession) -> Comment | None:
    query = select(Comment).filter_by(id=comment_id)
    db_comment = await db.execute(query)
    db_comment = db_comment.scalar_one_or_none()
    if db_comment:
        await db.delete(db_comment)
        await db.commit()
    return db_comment
