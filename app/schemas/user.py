from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from app.models import Role


class UserModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str = Field(min_length=6, max_length=25)


class UserDb(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    created_at: datetime
    avatar: str
    role: Role
    posts_number: int
    comments_number: int

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
