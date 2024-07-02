import enum
import os
from pathlib import Path

import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from app.models import Post
from app.models import User
from app.services.gravatar import get_gravatar
# from app.conf import config
from app.conf.config import settings

# cloudinary.config(
#     cloud_name=config.CLOUDINARY_NAME,
#     api_key=config.CLOUDINARY_KEY,
#     api_secret=config.CLOUDINARY_SECRET,
#     secure=True,
# )
cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)

class Effect(enum.Enum):
    sepia = "sepia"
    grayscale = "grayscale"


CLOUDINARY_FOLDER = "project_web21"
# folder structure:
# avatar: project_web21/user_id/avatar
# photo: project_web21/user_id/photos/post_id - name phone post_id


async def upload_avatar(
    img_file: UploadFile,
    user: User,
):
    """
    Upload user avatar.

    Args:
        img_file (UploadFile):  New picture.
        user (User):  Database object User
    Returns:
        str:  Cloudinary URL
    """    
    public_id = f"{CLOUDINARY_FOLDER}/{user.id}/avatar"

    try:
        res = cloudinary.uploader.upload(
            img_file.file, public_id=public_id, overwrite=True
        )
        gravatar_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=res.get("version")
        )
    except Exception as err:
        gravatar_url = await get_gravatar(user.email)

    return gravatar_url


async def delete_avatar(public_id: str):
    """
    Delete avatar

    Delete pictute in Cloudinary

    Args:
        public_id (str):  User id
    Returns:
        None:  None
    """    
    try:
        res = await cloudinary.uploader.destroy(public_id)
    except Exception as err:
        raise err
    return res


def upload_photo(
    img_file: UploadFile,
    post: Post,
):
    """
    Upload photo to Cloudinary

    Args:
        img_file (UploadFile):  Picture.
        post (Post):  Database object Post.
    Returns:
        str, str:  Cloudinary URL, public id
    """    
    public_id = f"{CLOUDINARY_FOLDER}/{post.user_id}/photos/{post.id}"

    try:
        res = cloudinary.uploader.upload(
            img_file.file, public_id=public_id, overwrite=True
        )
    except Exception as err:
        raise err

    # post.photo_public_id = res.get("public_id")
    # post.photo = res.get("secure_url", None)
    photo_public_id = res.get("public_id")
    photo_url = res.get("secure_url", None)
    return photo_url, photo_public_id


async def delete_photo(public_id: str) -> dict:
    """
    Delete photo by public id

    Args:
        public_id (str):  Public id.
    Returns:
        None:  None
    """    
    try:
        res = await cloudinary.uploader.destroy(public_id)
    except Exception as err:
        raise err
    return res


async def transform_photo(effect: Effect, post: Post) -> str:
    """
    Transform photo

    Args:
        effect (Effect):  Photo effect.
        post (Post):  Database object Post.
    Returns:
        str:  URL
    """    
    transformation = [{"effect": effect.value}]
    transform_url = cloudinary.CloudinaryImage(post.photo_public_id).build_url(
        transformation=transformation
    )
    return transform_url


# res = {
#     "asset_id": "ed09e17caf6edb35c55f4aa3116377fc",
#     "public_id": "project_web21/users/1/avatar",
#     "version": 1718922320,
#     "version_id": "456bc07619bca148ad419d75ca6126d1",
#     "signature": "42a1a7bbc58238b6bc5465c97b928b139a1a1415",
#     "width": 4096,
#     "height": 4096,
#     "format": "jpg",
#     "resource_type": "image",
#     "created_at": "2024-06-20T22:25:20Z",
#     "tags": [],
#     "bytes": 1855514,
#     "type": "upload",
#     "etag": "9fc9764cc824816909f9449ceec89595",
#     "placeholder": False,
#     "url": "http://res.cloudinary.com/dgknpebae/image/upload/v1718922320/project_web21/users/1/avatar.jpg",
#     "secure_url": "https://res.cloudinary.com/dgknpebae/image/upload/v1718922320/project_web21/users/1/avatar.jpg",
#     "folder": "project_web21/users/1",
#     "overwritten": True,
#     "original_filename": "1",
#     "api_key": "378313744372551",
# }

