from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime
)
from sqlalchemy.orm import relationship

from app.models import Base, Post , User

class Rating(Base):
    __tablename__= "ratings"

    id = Column(Integer, primary_key=True)
    rate = Column(Integer)
    post_id = Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"))
    post = relationship("Post", backref="ratings", lazy="selectin")
    user_id = Column("user_id", ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", backref="ratings", lazy="selectin")
    create_at = Column(DateTime)
