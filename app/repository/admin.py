from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models import Post
from app.services.cloudinary import upload_photo
from app.repository.tags import get_list_of_tags_by_string


async def delete_post_by_id(post_id: int, db: Session) -> Post | None:
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
