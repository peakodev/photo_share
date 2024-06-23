from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Table,
    func
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


post_m2m_tag = Table(
    "post_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"))
)


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
    # comments = relationship("Comment")
    # posts = relationship("Post")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    text = Column(String(32), nullable=False)


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    photo = Column(String(255), nullable=False)
    photo_url = Column(String(255))
    photo_public_id = Column(Integer)
    transform_url = Column(String(255))
    description = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    # comments = relationship("Comment")
    tags = relationship("Tag", secondary=post_m2m_tag, backref="posts")
    rating = Column(Integer)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref="posts", lazy="selectin")


class Comment(Base):
    __tablename__= "comments"
    id= Column(Integer,primary_key=True, index=True)
    text = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    post_id = Column('post_id', ForeignKey("posts.id", ondelete='CASCADE'), default=None)
    post = relationship('Post', backref="comments", lazy="selectin")
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref="comments", lazy="selectin")



