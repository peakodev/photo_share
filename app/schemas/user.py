from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from app.models import Role


class UserModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str = Field(min_length=6, max_length=25)


class ResetPasswordModel(BaseModel):
    token: str
    password: str = Field(min_length=6, max_length=25)

class ConfirmEmailModel(BaseModel):
    token: str

class UserUpdateModel(BaseModel):
    id: int
    first_name: str | None
    last_name: str | None
    email: str | None
    avatar: str | None


class UserSignupSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = EmailStr
    password: str = Field(min_length=6, max_length=25)


class UserDb(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    created_at: datetime
    avatar: str
    role: Role
    banned: bool
    posts_number: int
    comments_number: int

    class Config:
        from_attributes = True


class PublicUserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    avatar: str


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
