from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List
from fastapi import UploadFile

from app.models import Post
from app.models import User
from app.models import Comment
from app.services.cloudinary import upload_photo, transform_photo
from app.repository.tags import get_list_of_tags_by_string


async def get_all_posts(limit: int, offset: int, db: Session) -> List[Post]:
    # Query to get post id and its corresponding comment count
    comments_count_subquery = db.query(
        Comment.post_id,
        func.count(Comment.id).label("comment_count")
    ).group_by(Comment.post_id).subquery()
    
    # Query to join posts with the comment counts
    posts_with_comments_count = db.query(
        Post,
        func.coalesce(comments_count_subquery.c.comment_count, 0).label("comment_count")
    ).outerjoin(
        comments_count_subquery, Post.id == comments_count_subquery.c.post_id
    ).offset(offset).limit(limit).all()

    for post, comments_count in posts_with_comments_count:
        post.comments_count = comments_count
    posts = [post for post, comments_count in posts_with_comments_count]

    return posts


async def get_posts(limit: int, offset: int, user: User, db: Session) -> List[Post]:
    # Query to get post id and its corresponding comment count
    comments_count_subquery = db.query(
        Comment.post_id,
        func.count(Comment.id).label("comment_count")
    ).group_by(Comment.post_id).subquery()
    
    # Query to join posts with the comment counts
    posts_with_comments_count = db.query(
        Post,
        func.coalesce(comments_count_subquery.c.comment_count, 0).label("comment_count")
    ).outerjoin(
        comments_count_subquery, Post.id == comments_count_subquery.c.post_id
    ).filter(Post.user == user).offset(offset).limit(limit).all()
    
    for post, comments_count in posts_with_comments_count:
        post.comments_count = comments_count
    posts = [post for post, comments_count in posts_with_comments_count]

    return posts


# return post by id for current user
async def get_post_by_id(post_id: int, db: Session) -> Post | None:
    post = db.query(Post).filter_by(id=post_id).first()
    if post:
        comments_count = db.query(Comment).filter(Comment.post_id == post_id).count()
        post.comments_count = comments_count
    return post


async def find_posts(find_str: str, user: User, db: Session) -> List[Post]:
    return (
        db.query(Post)
        .filter(and_(Post.description.like(f"%{find_str}%"), Post.user == user))
        .all()
    )


async def create_post(
    description: str, tags: str, file: UploadFile, user: User, db: Session
) -> Post:

    tags = await get_list_of_tags_by_string(tags, db)

    new_post = Post(description=description, user=user, tags=tags)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    new_post.photo_url, new_post.photo_public_id = upload_photo(file, new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


async def update_post(
    post_id: int,
    user: User,
    db: Session,
    description: str = None,
    tags: str = None,
    effect=None,
    file: UploadFile = None,
) -> Post:

    post = db.query(Post).filter_by(id=post_id).first()
    if description:
        post.description = description
    if file:
        post.photo_url, post.photo_public_id = upload_photo(file, post)
    if tags:
        tags = await get_list_of_tags_by_string(tags, db)
        post.tags = tags
    if effect:
        post.transform_url = transform_photo(post, effect)
    post.updated_at = datetime.now()
    db.commit()
    db.refresh(post)
    return post


async def delete_post(post_id: int, user: User, db: Session) -> Post:
    post = db.query(Post).filter_by(id=post_id).first()
    db.delete(post)
    db.commit()
    return post
