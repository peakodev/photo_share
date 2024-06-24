from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from fastapi import UploadFile

from app.models import Post
from app.models import User
from app.services.cloudinary import upload_photo, transform_photo
from app.repository.tags import get_list_of_tags_by_string


# return list of posts for curent user
async def get_posts(
    limit: int, offset: int, user: User, db: Session
) -> List[Post]:
    return db.query(Post).filter_by(user=user).offset(offset).limit(limit).all()


# return list of posts of all users
async def get_all_posts(limit: int, offset: int, db: Session) -> List[Post]:
    return db.query(Post).offset(offset).limit(limit).all()


# return post by id for current user
async def get_post(post_id: int, user: User, db: Session) -> Post | None:
    return db.query(Post).filter_by(id=post_id, user=user).first()


async def find_posts(find_str: str, user: User, db: Session) -> List[Post]:
    return db.query(Post).filter(and_(Post.description.like(f'%{find_str}%'),Post.user==user)).all()


async def create_post(description: str, tags: str, file: UploadFile, user: User, db: Session) -> Post:

    tags = await get_list_of_tags_by_string(tags, db)

    new_post = Post(description=description, user=user, tags=tags)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    new_post.photo_url, new_post.photo_public_id = upload_photo(file, new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


async def update_post(post_id: int, user: User, db: Session, description: str = None,
                      tags: str = None, effect=None, file: UploadFile = None) -> Post | None:
    post = db.query(Post).filter_by(id=post_id, user=user).first()

    if post:
        if description:
            post.description = description
        if file:
            post.photo_url, post.photo_public_id = upload_photo(file, post)
        # TODO: now it delete old tags and add new from update method.
        if tags:
            tags = await get_list_of_tags_by_string(tags, db)
            post.tags = tags
        if effect:
            post.transform_url = transform_photo(post, effect)
        post.updated_at = datetime.now()
        db.commit()
        db.refresh(post)
    return post


async def delete_post(post_id: int, user: User, db: Session) -> Post | None:
    post = db.query(Post).filter_by(id=post_id, user=user).first()
    if post:
        db.delete(post)
        db.commit()
    return post
