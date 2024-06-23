from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.models import Post, User, Tag, Comment


# return list of posts for curent user
async def get_posts(
    limit: int, offset: int, user: User, db: AsyncSession
) -> List[Post]:

    query = (
        select(Post)
        .filter_by(user=user)
        .options(selectinload(Post.comments), selectinload(Post.tags))
        .offset(offset)
        .limit(limit)
    )
    posts = await db.execute(query)
    return posts.scalars().all()


# return list of posts of all users
async def get_all_posts(limit: int, offset: int, db: AsyncSession) -> List[Post]:

    query = (
        select(Post)
        .options(selectinload(Post.comments), selectinload(Post.tags))
        .offset(offset)
        .limit(limit)
    )
    posts = await db.execute(query)
    return posts.scalars().all()


# return post by id for current user
async def get_post(post_id: int, user: User, db: AsyncSession) -> Post | None:

    query = (
        select(Post)
        .filter_by(id=post_id, user=user)
        .options(selectinload(Post.comments), selectinload(Post.tags))
    )
    post = await db.execute(query)
    return post.scalar_one_or_none()


async def find_posts(find_str: str, user: User, db: AsyncSession) -> List[Post]:

    query = (
        select(Post)
        .filter_by(user=user)
        .filter(Post.description.contains(find_str))
        .options(selectinload(Post.comments), selectinload(Post.tags))
    )
    posts = await db.execute(query)
    return posts.scalars().all()


async def check_tags(tags: list[str], db: AsyncSession):
    validated_tags = []
    if len(tags) == 0:
        return validated_tags
    for item in tags:
        query = select(Tag).filter_by(text=item)
        result = await db.execute(query)
        tag = result.scalar_one_or_none()
        if tag is None:
            tag = Tag(text=item)
            db.add(tag)
            await db.commit()
            await db.refresh(tag)
        validated_tags.append(tag)
    return validated_tags


async def create_post(
    url: str, description, tags, user: User, db: AsyncSession
) -> Post:

    tags = await check_tags(tags, db)
    new_post = Post(description=description, user=user, photo=url, tags=tags)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    query = (
        select(Post)
        .filter_by(id=new_post.id, user=user)
        .options(selectinload(Post.tags))
    )
    p = await db.execute(query)
    current_post = p.scalar_one()
    return current_post


async def update_post(
    post_id: int, user: User, db: AsyncSession, description, tags, photo_url
) -> Post | None:

    query = (
        select(Post)
        .filter_by(id=post_id, user=user)
        .options(selectinload(Post.comments), selectinload(Post.tags))
    )
    p = await db.execute(query)
    post = p.scalar_one_or_none()
    if post:
        if description:
            post.description = description
        if photo_url:
            post.photo = photo_url
        # TODO: now it delete old tags and add new from update method.
        if tags:
            post.tags = await check_tags(tags, db)
        await db.commit()
        await db.refresh(post)
    return post


async def delete_post(post_id: int, user: User, db: AsyncSession) -> Post | None:

    query = (
        select(Post)
        .filter_by(id=post_id, user=user)
        .options(selectinload(Post.comments), selectinload(Post.tags))
    )
    post = await db.execute(query)
    post = post.scalar_one_or_none()
    if post:
        await db.delete(post)
        await db.commit()
    return post
