from sqlalchemy import (
    Column,
    Integer,
    String,
)

from app.models import Base


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    text = Column(String(32), nullable=False)
