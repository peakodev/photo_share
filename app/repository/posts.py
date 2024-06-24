from datetime import datetime

# from sqlalchemy import select
from sqlalchemy.orm import selectinload, Session
from sqlalchemy import and_
# from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import UploadFile

from app.models import Post
from app.models import User
from app.services.cloudinary import Effect, upload_photo, transform_photo
from app.repository.tags import get_list_of_tags_by_string


# return list of posts for curent user
async def get_posts(
    limit: int, offset: int, user: User, db: Session
) -> List[Post]:
    return db.query(Post).filter_by(user = user).offset(offset).limit(limit).all()

    # query = (
    #     select(Post)
    #     .filter_by(user=user)
    #     .options(selectinload(Post.comments), selectinload(Post.tags))
    #     .offset(offset)
    #     .limit(limit)
    # )
    # posts = db.execute(query)
    # return posts.scalars().all()


# return list of posts of all users
async def get_all_posts(limit: int, offset: int, db: Session) -> List[Post]:
    return db.query(Post).offset(offset).limit(limit).all()
    # query = (
    #     select(Post)
    #     .options(selectinload(Post.comments), selectinload(Post.tags))
    #     .offset(offset)
    #     .limit(limit)
    # )
    # posts = db.execute(query)
    # return posts.scalars().all()


# return post by id for current user
async def get_post(post_id: int, user: User, db: Session) -> Post | None:
    return db.query(Post).filter_by(id=post_id, user=user).first()
    # query = (
    #     select(Post)
    #     .filter_by(id=post_id, user=user)
    #     .options(selectinload(Post.comments), selectinload(Post.tags))
    # )
    # post = db.execute(query)
    # return post.scalar_one_or_none()


async def find_posts(find_str: str, user: User, db: Session) -> List[Post]:
    return db.query(Post).filter(and_(Post.description.like(f'%{find_str}%'),Post.user==user)).all()
    # query = (
    #     select(Post)
    #     .filter_by(user=user)
    #     .filter(Post.description.contains(find_str))
    #     .options(selectinload(Post.comments), selectinload(Post.tags))
    # )
    # posts = db.execute(query)
    # return posts.scalars().all()

async def create_post(description: str, tags: str, file: UploadFile, user: User, db: Session) -> Post:

    tags = await get_list_of_tags_by_string(tags, db)

    new_post = Post(description=description, user=user, tags=tags)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    new_post.photo_url, new_post.photo_public_id = upload_photo(file, new_post)
    db.commit()
    db.refresh(new_post)
    # ??? 
    # query = (
    #     select(Post)
    #     .filter_by(id=new_post.id, user=user)
    #     .options(selectinload(Post.tags))
    # )
    # p = db.execute(query)
    # current_post = p.scalar_one()
    # print(current_post, new_post)
    return new_post


async def update_post(
                        post_id: int,
                        user: User,
                        db: Session,
                        description: str = None,
                        tags: str = None,
                        effect = None,
                        file: UploadFile = None
                                        ) -> Post | None:
    post = db.query(Post).filter_by(id=post_id, user=user).first()
    # query = (
    #     select(Post)
    #     .filter_by(id=post_id, user=user)
    #     .options(selectinload(Post.comments), selectinload(Post.tags))
    # )
    # p = db.execute(query)
    # post = p.scalar_one_or_none()
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
    # query = (
    #     select(Post)
    #     .filter_by(id=post_id, user=user)
    #     .options(selectinload(Post.comments), selectinload(Post.tags))
    # )
    # post = await db.execute(query)
    # post = post.scalar_one_or_none()
    if post:
        db.delete(post) # await for async db
        db.commit() # await for async db
    return post
