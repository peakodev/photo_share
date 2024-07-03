import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import UploadFile
from app.models import User, Post
from io import BytesIO

from app.services.cloudinary import (
    upload_avatar,
    delete_avatar,
    upload_photo,
    delete_photo,
    transform_photo,
    Effect
)


@pytest.fixture
def user():
    return User(
        id=1,
        first_name="John",
        last_name="Doe",
        email="johndoe@example.com",
    )


@pytest.fixture
def post(user):
    return Post(
        id=1,
        user_id=user.id,
        description="Test post",
    )


@pytest.fixture
def img_file():
    return UploadFile(filename="test.jpg", file=BytesIO(b"test image content"))


@pytest.mark.asyncio
@patch("app.services.cloudinary.cloudinary.uploader.upload")
@patch("app.services.cloudinary.cloudinary.CloudinaryImage.build_url")
async def test_upload_avatar(mock_build_url, mock_upload, img_file, user):
    mock_upload.return_value = {"version": 123}
    mock_build_url.return_value = "http://example.com/avatar.jpg"

    result = await upload_avatar(img_file, user)

    assert result == "http://example.com/avatar.jpg"
    mock_upload.assert_called_once()
    mock_build_url.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.cloudinary.cloudinary.uploader.destroy", new_callable=AsyncMock)
async def test_delete_avatar(mock_destroy):
    mock_destroy.return_value = {"result": "ok"}

    result = await delete_avatar("public_id")

    assert result == {"result": "ok"}
    mock_destroy.assert_called_once_with("public_id")


@patch("app.services.cloudinary.cloudinary.uploader.upload")
def test_upload_photo(mock_upload, img_file, post):
    mock_upload.return_value = {
        "public_id": "public_id",
        "secure_url": "http://example.com/photo.jpg"
    }

    result = upload_photo(img_file, post)

    assert result == ("http://example.com/photo.jpg", "public_id")
    mock_upload.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.cloudinary.cloudinary.uploader.destroy", new_callable=AsyncMock)
async def test_delete_photo(mock_destroy):
    mock_destroy.return_value = {"result": "ok"}

    result = await delete_photo("public_id")

    assert result == {"result": "ok"}
    mock_destroy.assert_called_once_with("public_id")


@pytest.mark.asyncio
@patch("app.services.cloudinary.cloudinary.CloudinaryImage.build_url")
async def test_transform_photo(mock_build_url, post):
    mock_build_url.return_value = "http://example.com/transformed_photo.jpg"

    effect = Effect.sepia
    result = await transform_photo(effect, post)
    print(result)

    assert result == "http://example.com/transformed_photo.jpg"
    mock_build_url.assert_called_once_with(transformation=[{"effect": effect.value}])


if __name__ == "__main__":
    pytest.main()
