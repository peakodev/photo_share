from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import get_db, User, Post, Role
from app.services.auth import auth_service
from app.schemas.comments import CommentCreate, CommentUpdate, Comment
from app.repository import comments as repository_comments

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post(
    "/create",
    response_model=Comment,
    status_code=status.HTTP_201_CREATED,
    name="create_comments",
)
async def create_comment(
    body: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Create comment for post.

    CommentCreate schema {
                          post_id: int
                          text: str
                          }

    Args:
        body (CommentCreate):  Schema.
        db (Session, optional):  The database session.
        current_user (User, optional):  Current user

    Raises:
        HTTPException:  HTTP_400_BAD_REQUEST
        HTTPException:  HTTP_404_NOT_FOUND
    Returns:

        Comment:  Database object Comment.
    """
    print(f"api create comments {body=}")
    query = select(Post).filter_by(id=body.post_id)
    p = db.execute(query)
    db_post = p.scalar_one_or_none()
    if not body.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Comment can't be empty"
        )
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db_comment = await repository_comments.create_comment(body, current_user.id, db)
    return db_comment


@router.get("/{comment_id}", response_model=Comment)
async def get_comment_by_id(comment_id: int, db: Session = Depends(get_db)):
    """
    Get comment by id

    Args:
        comment_id (int):  Database object Coment.id to search.
        db (Session, optional):  The database session.
    Raises:
        HTTPException:  HTTP_404_NOT_FOUND
    Returns:
        Comment:  Database object Comment.

    """
    db_comment = await repository_comments.get_comment_by_id(comment_id, db)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment


@router.get("/post/{post_id}", response_model=list[Comment])
async def get_comments_by_post(
    post_id: int,
    offset: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_db),
):
    """
    Get comment by id

    Args:
        comment_id (int):  Database object Coment.id to search.
        db (Session, optional):  The database session.
    Raises:
        HTTPException:  HTTP_404_NOT_FOUND
    Returns:
        Comment:  Database object Comment.

    """
    comments = await repository_comments.get_comments_by_post(
        post_id, offset, limit, db
    )
    return comments


@router.put("/{comment_id}", response_model=Comment)
async def update_comment(
    comment_id: int,
    comment: CommentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Update comment.

    Only the owner or admin can update a comment.

    CommentUpdate schema (text: Optional[str] = None)

    Args:
        comment_id (int):  Database object Comment.id to update.
        comment (CommentUpdate):  Schema.
        db (Session, optional):  The database session.
        user (User, optional):  Commentator.
    Raises:
        HTTPException:  HTTP_400_BAD_REQUEST.
        HTTPException:  HTTP_403_FORBIDDEN.
        HTTPException:  HTTP_404_NOT_FOUND.
    Returns:
        Comment:  Database object Comment.
    """
    comment_db = await repository_comments.get_comment_by_id(comment_id, db)
    if comment_db is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if not comment.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Comment can't be empty"
        )
    if user.id == comment_db.user_id:
        comment = await repository_comments.update_comment(comment_id, comment, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You can't update  comment of user {comment_db.user.email}",
        )

    return comment


@router.delete("/{comment_id}", response_model=Comment)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Delete comment

    Only the owner or admin can delete a comment.

    Args:
    comment_id (int):  Database object Comment.id to delete.
    db (Session, optional):  The database session.
    user (User, optional):  Current user.
    Raises:
        HTTPException:  HTTP_403_FORBIDDEN.
        HTTPException:  HTTP_404_NOT_FOUND.
    Returns:
        Comment:  Database object Comment.
    """
    comment = await repository_comments.get_comment_by_id(comment_id, db)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if user.role in (Role.admin, Role.moderator):
        comment = await repository_comments.delete_comment(comment_id, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can't delete comments"
        )

    return comment
