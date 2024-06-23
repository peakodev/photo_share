from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.orm import relationship

from app.models import Base


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    post_id = Column(Integer, ForeignKey("posts.id"))
    post = relationship("Post", back_populates="comments")
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref="comments")
