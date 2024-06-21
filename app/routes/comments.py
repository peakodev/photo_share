from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.post import Post
from app.services.auth import Auth
from app.schemas.comments import CommentCreate, CommentUpdate, Comment
from app.repository import comments_crud as crud

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/create/", response_model=Comment)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    return crud.create_comment(db=db, comment=comment)


@router.get("/comments/{comment_id}", response_model=Comment)
def get_comment_by_id(comment_id: int, db: Session = Depends(get_db)):
    db_comment = crud.get_comment(db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment


@router.get("/comments/", response_model=list[Comment])
def get_comment_by_post(post_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    comments = crud.get_comments_by_post(db, post_id=post_id, skip=skip, limit=limit)
    return comments


@router.put("/comments/{comment_id}", response_model=Comment)
def update_comment(comment_id: int, comment: CommentUpdate, db: Session = Depends(get_db)):
    db_comment = crud.update_comment(db=db, comment_id=comment_id, comment=comment)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment


@router.delete("/comments/{comment_id}", response_model=Comment)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = crud.delete_comment(db=db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment
