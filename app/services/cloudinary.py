import enum
import os
from pathlib import Path

import cloudinary
import cloudinary.uploader

from app.database.post import Post
from app.database.user import User
from app.services.gravatar import get_gravatar
from app.conf import config

cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_KEY,
    api_secret=config.CLOUDINARY_SECRET,
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
    img_file: Path,
    user: User,
):
    dest_folder = f"{CLOUDINARY_FOLDER}/{user.id}/avatar"
    gravatar_url = None

    try:
        res = cloudinary.uploader.upload(
            img_file, public_id=dest_folder, overwrite=True
        )
    except Exception as err:
        gravatar_url = get_gravatar(user.email)

    if gravatar_url:
        # user.avatar_id = None
        user.avatar = gravatar_url
    else:
        # user.avatar_id = res.get("public_id", None)
        user.avatar = res.get("secure_url", None)


async def delete_avatar(public_id: str):
    try:
        res = await cloudinary.uploader.destroy(public_id)
    except Exception as err:
        raise err
    return res


async def upload_photo(
    img_file: Path,
    post: Post,
):
    public_id = f"{CLOUDINARY_FOLDER}/{post.user_id}/photos/{post.id}"

    try:
        res = await cloudinary.uploader.upload(
            img_file, public_id=public_id, overwrite=True
        )
    except Exception as err:
        raise err

    post.photo_id = res.get("public_id", None)
    post.photo = res.get("secure_url", None)


async def delete_photo(public_id: str) -> dict:
    try:
        res = cloudinary.uploader.destroy(public_id)
    except Exception as err:
        raise err
    return res


def transform_photo(effect: Effect, post: Post) -> str:
    transformation = [{"effect": effect.value}]
    url = cloudinary.CloudinaryImage(post.photo_public_id).build_url(
        transformation=transformation
    )
    # print(url)
    post.photo_transform_url = url
    # return url


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
