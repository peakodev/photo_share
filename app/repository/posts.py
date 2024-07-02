from datetime import datetime, date

from sqlalchemy.orm import Session, aliased, Query
from sqlalchemy import and_, or_, func, desc, asc, Date, cast
from typing import List
from fastapi import UploadFile

from app.models import Post, User, Comment, Tag, post_m2m_tag
from app.services.cloudinary import upload_photo, transform_photo
from app.repository.tags import (
    get_list_of_tags_by_string,
    search_tags_by_query,
    get_tags_by_name
)
from app.schemas.post import PostSearchSchema, OrderByEnum, OrderEnum


async def get_all_posts(limit: int, offset: int, db: Session) -> List[Post]:
    """
    Get all posts.

    :param limit: Limit.
    :type limit: int
    :param offset: Offset.
    :type offset: int
    :param db: The database session.
    :type db: Session
    :return: List of Database objects Post.
    :rtype: List[Post]
    """    
    # Query to get post id and its corresponding comment count
    comments_count_subquery = db.query(
        Comment.post_id,
        func.count(Comment.id).label("comment_count")
    ).group_by(Comment.post_id).subquery()
    
    # Query to join posts with the comment counts
    posts_with_comments_count = db.query(
        Post,
        func.coalesce(comments_count_subquery.c.comment_count, 0).label("comment_count")
    ).outerjoin(
        comments_count_subquery, Post.id == comments_count_subquery.c.post_id
    ).offset(offset).limit(limit).all()

    for post, comments_count in posts_with_comments_count:
        post.comments_count = comments_count
    posts = [post for post, comments_count in posts_with_comments_count]

    return posts


async def get_posts(limit: int, offset: int, user: User, db: Session) -> List[Post]:
    """
    Get posts of user.

    :param limit: Limit.
    :type limit: int
    :param offset: Offset.
    :type offset: int
    :param user: Database object User.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: Posts of user.
    :rtype: List[Post]
    """    
    # Query to get post id and its corresponding comment count
    comments_count_subquery = db.query(
        Comment.post_id,
        func.count(Comment.id).label("comment_count")
    ).group_by(Comment.post_id).subquery()
    
    # Query to join posts with the comment counts
    posts_with_comments_count = db.query(
        Post,
        func.coalesce(comments_count_subquery.c.comment_count, 0).label("comment_count")
    ).outerjoin(
        comments_count_subquery, Post.id == comments_count_subquery.c.post_id
    ).filter(Post.user == user).offset(offset).limit(limit).all()
    
    for post, comments_count in posts_with_comments_count:
        post.comments_count = comments_count
    posts = [post for post, comments_count in posts_with_comments_count]

    return posts


# return post by id for current user
async def get_post_by_id(post_id: int, db: Session) -> Post | None:
    """
    Get post by id.

    :param post_id: Database object Post.id to search.
    :type post_id: int
    :param db: The database session.
    :type db: Session
    :return: Database object Post.
    :rtype: Post | None
    """    
    post = db.query(Post).filter_by(id=post_id).first()
    if post:
        comments_count = db.query(Comment).filter(Comment.post_id == post_id).count()
        post.comments_count = comments_count
    return post


async def find_posts(find_str: str, user: User, db: Session) -> List[Post]:
    """
    Find posts of user by text in description.

    :param find_str: Text in Post.description to search.
    :type find_str: str
    :param user: Database object User.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: Posts of user.
    :rtype: List[Post]
    """    
    return (
        db.query(Post)
        .filter(and_(Post.description.like(f"%{find_str}%"), Post.user == user))
        .all()
    )


async def search_posts_by_inputs(input: PostSearchSchema, db: Session) -> List[Post]:
    """
    Search posts by inputs.

    PostSearchSchema schema {
                            query: Optional[str] = Field(None)\n
                            limit: int = 20\n
                            offset: int = 0\n
                            order: Optional[OrderEnum] = OrderEnum.desc\n
                            order_by: Optional[OrderByEnum] = OrderByEnum.created_at\n
                            filter: Optional[PostFilterSchema]\n
                            }
    OrderByEnum schema {
                        created_at = "created_at"\n
                        rating = "rating"\n
                        }
    OrderEnum schema {
                      asc = "asc"\n
                      desc = "desc"
                      }
    PostFilterSchema schema {
                            rating: Optional[int] = Field(None, ge=1, le=5)
                            tags: Optional[List[str]] = []
                            show_date: Optional[date] = None
                            }

    :param input: Schema.
    :type input: PostSearchSchema
    :param db: The database session.
    :type db: Session
    :return: List of Database objects Post.
    :rtype: List[Post]
    """    
    query = db.query(Post)

    # Initialize expression holder
    expr_post = None

    # Check if input.query is not empty
    if input.query and input.query.strip():
        expr_post = await __build_query_expression(input.query, db)

    # Check if input.filter.tags is not empty or None and apply filtering
    if input.filter.tags and any(tag.strip() for tag in input.filter.tags):
        expr_post = await __filter_by_tags(input.filter.tags, expr_post, db)

    # Check if input.filter.rating is not None and apply filtering
    if input.filter.rating:
        expr_post = await __filter_by_rating(input.filter.rating, expr_post)

    # Filter by show_date if provided
    if input.filter.show_date:
        expr_post = await __filter_by_show_date(input.filter.show_date, expr_post)

    # Apply the built expression to the query if it exists
    if expr_post is not None:
        query = query.filter(expr_post)

    # Handle ordering
    query = apply_ordering(query, input.order, input.order_by)

    return query.all()


async def __build_query_expression(query: str, db: Session):
    """
    Internal function for def search_posts_by_inputs

    Check if input.query is not empty

    :type query: str
    :param db: The database session.
    :type db: Session
    :return:  Query to database
    :rtype: Query
    """    
    tags_queried = await search_tags_by_query(query, db)
    expr_post = Post.description.ilike(f"%{query}%")
    if tags_queried:
        expr_post = or_(expr_post, Post.tags.any(Tag.id.in_([tag.id for tag in tags_queried])))
    return expr_post


async def __filter_by_tags(tag_names: List[str], expr_post, db: Session):
    """
    Internal function for def search_posts_by_inputs

    Check if input.filter.tags is not empty or None and apply filtering

    :param tag_names: List of tags text.
    :type tag_names: List[str]
    :param expr_post: Query to database.
    :type expr_post: Query
    :param db: The database session.
    :type db: Session
    :return: Query to database.
    :rtype: Query
    """    
    tags = await get_tags_by_name(tag_names, db)
    expr_tags = Post.tags.any(Tag.id.in_([tag.id for tag in tags]))
    return and_(expr_post, expr_tags) if expr_post is not None else expr_tags


async def __filter_by_rating(rating: int, expr_post):
    """
    Internal function for def search_posts_by_inputs

    Check if input.filter.rating is not None and apply filtering

    :param rating: Rating of Post.
    :type rating: int
    :param expr_post: Query to database.
    :type expr_post: Query
    :return: Query to database.
    :rtype: Query
    """    
    # Rating shound be between rating and rating + 1
    expr_rating = (Post.rating >= rating) & (Post.rating < rating + 1)
    return and_(expr_post, expr_rating) if expr_post is not None else expr_rating


async def __filter_by_show_date(show_date: date, expr_post):
    """
    Internal function for def search_posts_by_inputs

    Filter by show_date if provided

    :param show_date: Date of create Post
    :type show_date: date
    :param expr_post: Filter results.
    :type expr_post: List[Post] | None
    :return: List of Database objects Post.
    :rtype: List[Post] | None
    """    
    expr_show_date = cast(Post.created_at, Date) == show_date
    return and_(expr_post, expr_show_date) if expr_post is not None else expr_show_date


def apply_ordering(query: Query, order: OrderEnum, order_by: OrderByEnum) -> Query:

    """
    Internal function for def search_posts_by_inputs

    Handle ordering

    :return: Query to database.
    :rtype: Query
    """
    order_func = desc if order == OrderEnum.desc else asc
    if order_by == OrderByEnum.rating:
        query = query.order_by(order_func(Post.rating))
    elif order_by == OrderByEnum.created_at:
        query = query.order_by(order_func(Post.created_at))
    return query


async def create_post(
    description: str, tags: str, file: UploadFile, user: User, db: Session
) -> Post:
    """
    Create new post

    :param description: Description for Post.
    :type description: str
    :param tags: Tags for Post.
    :type tags: str
    :param file: Photo for Post.
    :type file: UploadFile
    :param user: Owner.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: Database object Post.
    :rtype: Post
    """    

    tags = await get_list_of_tags_by_string(tags, db)

    new_post = Post(description=description, user=user, tags=tags)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    new_post.photo_url, new_post.photo_public_id = upload_photo(file, new_post)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


async def update_post(
    post_id: int,
    user: User,
    db: Session,
    description: str = None,
    tags: str = None,
    effect=None,
    file: UploadFile = None,
) -> Post:
    """
    Update post by id.

    Parameters are optional.

    :param post_id: Database object Post.id to update.
    :type post_id: int
    :param user: Owner.
    :type user: User
    :param db: The database session.
    :type db: Session
    :param description: New description for post. 
    :type description: str, optional
    :param tags: New tag\\s for post.
    :type tags: str, optional
    :param effect: New effect to picture in Post.
    :type effect: str, optional
    :param file: New picture for post.
    :type file: UploadFile, optional
    :return: Updated database object Post.
    :rtype: Post
    """
    post = db.query(Post).filter_by(id=post_id).first()
    if description:
        post.description = description
    if file:
        post.photo_url, post.photo_public_id = upload_photo(file, post)
    if tags:
        tags = await get_list_of_tags_by_string(tags, db)
        post.tags = tags
    if effect:
        post.transform_url = await transform_photo(effect, post)
    post.updated_at = datetime.now()
    db.commit()
    db.refresh(post)
    return post


async def delete_post(post_id: int, user: User, db: Session) -> Post:
    """
    Delete post by id. 

    :param post_id: Database object Post.id to delete.
    :type post_id: int
    :param user: Owner.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: Database object Post.
    :rtype: Post
    """    
    post = db.query(Post).filter_by(id=post_id).first()
    db.delete(post)
    db.commit()
    return post
