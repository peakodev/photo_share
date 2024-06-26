from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


from app.schemas.user import UserDb
from app.models import Tag

from app.schemas.comments import Comment, CommentUpdate


class TagResponse(BaseModel):
    id: int
    text: str

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
    tags: list[TagResponse]
    class Config:
        from_attributes = True


class PostResponse(PostCreateResponse):
    comments: list[Comment]

    class Config:
        from_attributes = True



