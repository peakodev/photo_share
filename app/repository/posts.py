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

    Args:
        limit (int):  Limit.
        offset (int):  Offset.
        db (Session):  The database session.
    Returns:
        List[Post]:  List of Database objects Post.
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

    Args:
        limit (int):  Limit.
        offset (int):  Offset.
        user (User):  Database object User.
        db (Session):  The database session.
    Returns:
        List[Post]:  Posts of user.
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

    Args:
        post_id (int):  Database object Post.id to search.
        db (Session):  The database session.
    Returns:
        Post | None:  Database object Post.
    """    
    post = db.query(Post).filter_by(id=post_id).first()
    if post:
        comments_count = db.query(Comment).filter(Comment.post_id == post_id).count()
        post.comments_count = comments_count
    return post


async def find_posts(find_str: str, user: User, db: Session) -> List[Post]:
    """
    Find posts of user by text in description.

    Args:
        find_str (str):  Text in Post.description to search.
        user (User):  Database object User.
        db (Session):  The database session.
    Returns:
        List[Post]:  Posts of user.
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
                            query: Optional[str] = Field(None),
                            limit: int = 20,
                            offset: int = 0,
                            order: Optional[OrderEnum] = OrderEnum.desc,
                            order_by: Optional[OrderByEnum] = OrderByEnum.created_at,
                            filter: Optional[PostFilterSchema]
                            }
    OrderByEnum schema {
                        created_at = "created_at",
                        rating = "rating",
                        }
    OrderEnum schema {
                      asc = "asc",
                      desc = "desc"
                      }
    PostFilterSchema schema {
                            rating: Optional[int] = Field(None, ge=1, le=5),
                            tags: Optional[List[str]] = [],
                            show_date: Optional[date] = None
                            }

    Args:
        input (PostSearchSchema):  Schema.
        db (Session):  The database session.
    Returns:
        List[Post]:  List of Database objects Post.
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

    Args:
        query (str): query
        db (Session): The database session.

    Returns:
        Query: Query to database
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

    Args:
        tag_names (List[str]):  List of tags text.
        expr_post (Query):  Query to database.
        db (Session):  The database session.
    Returns:
        Query:  Query to database.
    """    
    tags = await get_tags_by_name(tag_names, db)
    expr_tags = Post.tags.any(Tag.id.in_([tag.id for tag in tags]))
    return and_(expr_post, expr_tags) if expr_post is not None else expr_tags


async def __filter_by_rating(rating: int, expr_post):
    """
    Internal function for def search_posts_by_inputs

    Check if input.filter.rating is not None and apply filtering

    Args:
        rating (int):  Rating of Post.
        expr_post (Query):  Query to database.
    Returns:
        Query:  Query to database.
    """    
    # Rating shound be between rating and rating + 1
    expr_rating = (Post.rating >= rating) & (Post.rating < rating + 1)
    return and_(expr_post, expr_rating) if expr_post is not None else expr_rating


async def __filter_by_show_date(show_date: date, expr_post):
    """
    Internal function for def search_posts_by_inputs

    Filter by show_date if provided

    Args:
        show_date (date):  Date of create Post.
        expr_post (List[Post] | None):  Filter results.
    Returns:
        List[Post] | None:  List of Database objects Post.
    """    
    expr_show_date = cast(Post.created_at, Date) == show_date
    return and_(expr_post, expr_show_date) if expr_post is not None else expr_show_date


def apply_ordering(query: Query, order: OrderEnum, order_by: OrderByEnum) -> Query:

    """
    Internal function for def search_posts_by_inputs

    Handle ordering

    Returns:
        Query:  Query to database.
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

    Args:
        description (str):  Description for Post.
        tags (str):  Tags for Post.
        file (UploadFile):  Photo for Post.
        user (User):  Owner.
        db (Session):  The database session.
    Returns:
        Post:  Database object Post.
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

    Args:
        post_id (int):  Database object Post.id to update.
        user (User):  Owner.
        db (Session):  The database session.
        description (str, optional):  New description for post. 
        tags (str, optional):  New tag\'s for post.
        effect (str, optional):  New effect to picture in Post.
        file (UploadFile, optional):  New picture for post.
    Returns:
        Post:  Updated database object Post.
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

    Args:
        post_id (int):  Database object Post.id to delete.
        user (User):  Owner.
        db (Session):  The database session.
    Returns:
        Post:  Database object Post.
    """    
    post = db.query(Post).filter_by(id=post_id).first()
    db.delete(post)
    db.commit()
    return post
