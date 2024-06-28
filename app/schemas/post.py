from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import List, Optional
from enum import Enum


from app.schemas.user import UserDb, UserUpdateModel
from app.models import Tag

from app.schemas.comments import Comment
from app.schemas.tags import TagDB


class PostDeleteSchema(BaseModel):
    id: int


class PostSchema(BaseModel):
    description: str = Field(min_length=3, max_length=255)
    tags: List[str]


class PostCreateResponse(BaseModel):
    id: int
    photo_url: str | None
    user: UserDb
    description: str
    tags: List[TagDB]

    class Config:
        from_attributes = True


class PostResponse(PostCreateResponse):
    created_at: str
    updated_at: str
    comments_count: int
    tags: List[str]
    comments: List[Comment]
    user: UserUpdateModel

    @field_validator("created_at", mode="before")
    def parse_created_at(cls, value: datetime):
        value_str = value.strftime('%d-%m-%Y %H:%M:%S')
        return value_str

    @field_validator("updated_at", mode="before")
    def parse_updated_at(cls, value: datetime):
        value_str = value.strftime('%d-%m-%Y %H:%M:%S')
        return value_str

    @field_validator("tags", mode="before")
    def convert_tags_to_string(cls, value: list[Tag]):
        return [tag.text for tag in value]

    class Config:
        from_attributes = True


class OrderByEnum(str, Enum):
    created_at = "created_at"
    rating = "rating"


class OrderEnum(str, Enum):
    asc = "asc"
    desc = "desc"


class PostFilterSchema(BaseModel):
    tags: Optional[List[str]] = []
    show_date: Optional[date] = None


class PostSearchSchema(BaseModel):
    query: Optional[str] = Field(None, min_length=3, max_length=255)
    limit: int = 20
    offset: int = 0
    order: Optional[OrderEnum] = OrderEnum.desc
    order_by: Optional[OrderByEnum] = OrderByEnum.created_at
    filter: Optional[PostFilterSchema]
