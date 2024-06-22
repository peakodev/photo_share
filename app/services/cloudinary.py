import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from app.conf.config import settings


def cloudinary_upload(file: UploadFile, user_id):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
        )
    
    r = cloudinary.uploader.upload(
        file.file, public_id=f"users/{user_id}", overwrite=True
    )
    photo_url = cloudinary.CloudinaryImage(f"users/{user_id}").build_url(
        width=250, height=250, crop="fill", version=r.get("version")
    )
    return photo_url