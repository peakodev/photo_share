from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.models import Post
from app.models import User
from app.models import Tag


# return list of posts for curent user
async def get_posts(limit: int, offset: int, user: User, db: AsyncSession) -> List[Post]:

    query = select(Post).filter_by(user=user).offset(offset).limit(limit)
    posts =  db.execute(query)
    return posts.scalars().all()


# return list of posts of all users
async def get_all_posts(limit: int, offset: int, db: AsyncSession) -> List[Post]:

    query = select(Post).offset(offset).limit(limit)
    posts = await db.execute(query)
    return posts.scalars().all()


# return post by id for current user
async def get_post(post_id: int, user: User, db: AsyncSession) -> Post | None:

    query = select(Post).filter_by(id=post_id, user=user)
    post =  db.execute(query)
    return post.scalar_one_or_none()


async def find_posts(find_str: str, user: User, db: AsyncSession) -> List[Post]:

    query = (
        select(Post)
        .filter_by(user=user)
        .filter(Post.description.contains(find_str))
    )
    posts =  db.execute(query)
    return posts.scalars().all()


async def check_tags(tags: list[str], db: AsyncSession):
    validated_tags = []
    if len(tags) == 0:
        return validated_tags
    for item in tags:
        query =  select(Tag).filter_by(text=item)
        result = db.execute(query)
        tag = result.scalar_one_or_none()
        if tag is None:
            tag = Tag(text=item)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        validated_tags.append(tag)
    return validated_tags


async def create_post(url: str, description, tags, 
                      user: User, db: AsyncSession) -> Post:
    
    tags =  await check_tags(tags, db)   
    new_post = Post(description=description, user=user, photo=url, tags=tags)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


async def update_post(post_id: int, user: User, db: AsyncSession, 
                      description, tags, photo_url) -> Post | None:
    
    query = select(Post).filter_by(id=post_id, user=user)
    p =  db.execute(query)
    post = p.scalar_one_or_none()
    if post:
        if description:
            post.description = description
        if photo_url:
            post.photo = photo_url
# TODO: now it delete old tags and add new from update method. 
        if tags:
            post.tags = await check_tags(tags, db)
        db.commit()
        db.refresh(post)
    return post


async def delete_post(post_id: int, user: User, db: AsyncSession) -> Post | None:
    
    query = select(Post).filter_by(id=post_id, user=user)
    post =  db.execute(query)
    post = post.scalar_one_or_none()
    if post:
        db.delete(post)
        db.commit()
    return post