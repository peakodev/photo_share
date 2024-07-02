from datetime import date
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Table,
    func,
    Float
)
from sqlalchemy.orm import  Mapped, mapped_column, relationship

from app.models import Base

post_m2m_tag = Table(
    "post_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"))
)


class Post(Base):  
    """
    Post 

    Database object Post(id: int\n
                        photo_url: str,\n
                        photo_public_id: str,\n
                        transform_url: str,\n
                        description: str,\n
                        created_at: datatime,\n
                        updated_at: datatime,\n
                        tags: relationship(list[Tag]),\n
                        rating: float,\n
                        user_id: int,\n
                        user: relationship(User),\n
                        comments_count: int\n
                        )
    """    
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    photo_url = Column(String(255))
    photo_public_id = Column(String(255))
    transform_url = Column(String(255))
    description = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column("updated_at", DateTime, default=None, nullable=True, onupdate=func.now())
    tags = relationship("Tag", secondary=post_m2m_tag, backref="posts", lazy="selectin")
    rating = Column(Float)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref="posts", lazy="selectin")
    comments_count = 0
    comments = relationship('Comment', backref='post', lazy="selectin", cascade="all, delete-orphan")
    