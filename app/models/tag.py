from sqlalchemy import (
    Column,
    Integer,
    String,
)

from app.models import Base 
from app.models.post import post_m2m_tag
from sqlalchemy.orm import relationship

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    text = Column(String(32), nullable=False)
    # posts = relationship("Tag", secondary=post_m2m_tag, lazy="selectin")
