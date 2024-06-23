from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models import Tag
from app.models import get_db
from app.schemas.tags import TagDB
from app.repository.tags import get_tags, get_tag_by_text as repo_get_tag_by_text

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/all_tags", response_model=list[TagDB])
async def get_all_tags(db: Session = Depends(get_db)) -> list[Tag]:
    return await get_tags(db=db)


@router.get("/{query}", response_model=TagDB)
async def get_tag_by_text(query: str, db: Session = Depends(get_db)) -> Tag | None:
    return await repo_get_tag_by_text(query=query, db=db)
