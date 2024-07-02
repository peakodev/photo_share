from fastapi import HTTPException
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from datetime import datetime

from app.schemas.user import PublicUserResponse


class CommentBase(BaseModel):
    pass


class CommentCreate(BaseModel):
    post_id: int
    text: str


class CommentUpdate(BaseModel):
    text: Optional[str] = None


class CommentInDBBase(CommentBase):
    id: int
    created_at: str
    updated_at: str | None

    @field_validator("created_at", mode="before")
    def parse_created_at(cls, value: datetime):
        value_str = value.strftime('%d-%m-%Y %H:%M:%S')
        return value_str

    @field_validator("updated_at", mode="before")
    def parse_updated_at(cls, value: datetime | None):
        if value:
            value = value.strftime('%d-%m-%Y %H:%M:%S')
        return value
    
    class Config:
        from_attributes = True 


class Comment(CommentInDBBase):
    text: str
    post_id: int
    user: PublicUserResponse
