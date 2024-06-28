from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.schemas.user import UserDb


class CommentBase(BaseModel):
    pass


class CommentCreate(BaseModel):
    post_id: int
    text: str


class CommentUpdate(BaseModel):
    text: Optional[str] = None


class CommentInDBBase(CommentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 


class Comment(CommentInDBBase):
    text: str
    post_id: int
    user: UserDb


