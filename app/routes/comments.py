from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import get_db
from app.models import User
from app.models import Post
from app.services.auth import Auth
from app.schemas.comments import CommentCreate, CommentUpdate, Comment
from app.repository import comments_crud as crud

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/create/", response_model=Comment)
async def create_comment(comment: CommentCreate, post_id: int,  db: Session = Depends(get_db),
                         current_user: User = Depends(Auth.get_current_user)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return crud.create_comment(db=db, comment=comment, user_id=current_user.id, post_id=post_id)


@router.get("/{comment_id}", response_model=Comment)
async def get_comment_by_id(comment_id: int, db: Session = Depends(get_db)):
    db_comment = crud.get_comment(db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment


@router.get("/{post_id}", response_model=list[Comment])
async def get_comment_by_post(post_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    comments = crud.get_comments_by_post(db, post_id=post_id, skip=skip, limit=limit)
    return comments


@router.put("/{comment_id}", response_model=Comment)
async def update_comment(comment_id: int, comment: CommentUpdate, db: Session = Depends(get_db),
                         current_user: User = Depends(Auth.get_current_user)):
    db_comment = crud.get_comment(db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")

    db_comment = crud.update_comment(db=db, comment_id=comment_id, comment=comment)
    return db_comment


@router.delete("/{comment_id}", response_model=Comment)
async def delete_comment(comment_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(Auth.get_current_user)):
    db_comment = crud.delete_comment(db=db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment
