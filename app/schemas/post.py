from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


from app.schemas.user import UserDb, UserUpdateModel
from app.models import Tag

from app.schemas.comments import Comment, CommentUpdate
from app.schemas.tags import TagDB, TagModel

# class TagResponse(BaseModel):
#     id: int
#     text: str

class PostDeleteSchema(BaseModel):
    id: int

    
class PostSchema(BaseModel):
    description: str = Field(min_length=3, max_length=255)
    tags: list[str]


class PostCreateResponse(BaseModel):
    id: int
    photo_url: str | None
    user: UserDb
    description: str
    tags: list[TagDB]
    class Config:
        from_attributes = True


class PostResponse(PostCreateResponse):
    created_at: str
    updated_at: str
    comments_count: int
    tags: list[str]
    comments: list[Comment]
    user: UserUpdateModel

    @field_validator("created_at", mode="before")
    def parse_created_at(cls, value:datetime):
        value_str = value.strftime('%d-%m-%Y %H:%M:%S')
        return value_str
    
    @field_validator("updated_at", mode="before")
    def parse_updated_at(cls, value:datetime):
        value_str = value.strftime('%d-%m-%Y %H:%M:%S')
        return value_str
    
    @field_validator("tags", mode="before")
    def convert_tags_to_string(cls, value: list[Tag]):
        return [tag.text for tag in value]
    
    class Config:
        from_attributes = True

class RatingResponce(BaseModel):
    post_id: int
    rating: float


