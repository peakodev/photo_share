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
    """
    Comment 

    Database model Comment(id: int,\n
                        text: str,\n
                        create_at: datatime,\n
                        update_at: datatime,\n
                        post_id: int,\n
                        post: relationship(Post)\n
                        user_id: int\n
                        user: relationship(User)
                        )
    """    
    
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    post_id = Column('post_id', ForeignKey("posts.id", ondelete='CASCADE'), default=None)
    # post = relationship('Post', backref="comments", lazy="selectin")
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref="comments", lazy="selectin")
