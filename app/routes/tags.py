from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models import Tag, get_db
import app.repository.tags as tags_repo
from app.schemas.tags import TagDB

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/all_tags", response_model=list[TagDB])
async def get_all_tags(db: Session = Depends(get_db)) -> list[Tag]:
    return await tags_repo.get_tags(db=db)


@router.get("/{text}", response_model=TagDB | None)
async def get_tag_by_text(text: str, db: Session = Depends(get_db)) -> Tag | None:
    return await tags_repo.get_tag_by_text(text=text, db=db)
