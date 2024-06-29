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
from sqlalchemy.orm import relationship

from app.models import Base

post_m2m_tag = Table(
    "post_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"))
)


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    photo_url = Column(String(255))
    photo_public_id = Column(String(255))
    transform_url = Column(String(255))
    description = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    # comments = relationship("Comment")
    tags = relationship("Tag", secondary=post_m2m_tag, backref="posts", lazy="selectin")
    rating = Column(Float)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref="posts", lazy="selectin")
    comments_count = 0
