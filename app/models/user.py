from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    func,
    Boolean,
    Enum as EnumSQL,
)
from sqlalchemy.sql.sqltypes import DateTime

from app.models import Base


class Role(str, Enum):
    user: str = "user"
    admin: str = "admin"
    moderator: str = "moderator"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False, unique=True)
    first_name = Column(String(250), nullable=False)
    last_name = Column(String(250), nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(EnumSQL(Role), default=Role.user, nullable=False)
    banned = Column(Boolean, default=False, nullable=False)
    posts_number = 0
    comments_number = 0
