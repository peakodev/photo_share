from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models import Post
from app.services.cloudinary import upload_photo
from app.repository.tags import get_list_of_tags_by_string


async def delete_post_by_id(post_id: int, db: Session) -> Post | None:
    """
    Search post in database by id, if exist delete post.

    :param post_id: Database object Post.id to delete.
    :type post_id: int
    :param db: The database session.
    :type db: Session
    :return: Database object Post.
    :rtype: Post | None
    """    
    post = db.query(Post).filter_by(id=post_id).first()
    if post:
        db.delete(post)
        db.commit()
    return post


async def update_post_by_id(post_id: int,
                            db: Session,
                            photo: UploadFile = None,
                            description: str = None,
                            tags: str = None,
                            rating: int = None) -> Post | None:
    """
    Update post by id.

    Parameters are optional.

    :param post_id: Database object Post.id to update.
    :type post_id: int
    :param db: The database session.
    :type db: Session
    :param photo: New picture for post.
    :type photo: UploadFile, optional
    :param description: New description for post.
    :type description: str, optional
    :param tags: New tag\s for post.
    :type tags: str, optional
    :param rating: New rating for post.
    :type rating: int, optional
    :return: Database object Post.
    :rtype: Post | None
    """    
    post = db.query(Post).filter_by(id=post_id).first()
    if post:
        if photo:
            post.photo_url, post.photo_public_id = upload_photo(photo, post)
        if description:
            post.description = description
        if tags:
            tags = await get_list_of_tags_by_string(tags, db)
            post.tags = tags
        if rating:
            post.rating = rating
        db.commit()
        db.refresh(post)
    return post
