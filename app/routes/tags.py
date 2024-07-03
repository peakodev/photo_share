from fastapi import (APIRouter,
                     Depends,
                     HTTPException,
                     status)
from sqlalchemy.orm import Session

from app.models import Tag, get_db
from app.repository.tags import (get_tags,
                                 get_tag_by_text,
                                 create_tag_in_db,
                                 get_tag_by_id,
                                 get_list_of_tags_by_string)
from app.schemas.tags import TagDB, TagModel

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/all_tags/",response_model=list[TagDB])
async def get_all_tags(db: Session = Depends(get_db)) -> list[Tag]:
    """
    Return all tags from db

    Args:
        db (Session, optional):  The database session
    Returns:
        list[Tag]:  List of Database objects Tag
    """    
    return await get_tags(db=db)


@router.get("/tag_value/{text}",response_model=TagDB)
async def search_tag_by_text(text:str, db: Session = Depends(get_db)) -> Tag | None:
    """
    Search tag in db by value.

    Args:
        text (str):  Text for search.
        db (Session, optional):  The database session.
    Raises:
        HTTPException:  HTTP_404_NOT_FOUND
    Returns:
        Tag | None:  Database object Tag
    """    
    result = await get_tag_by_text(text=text, db=db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tag not found')
    return result


@router.post("", response_model=TagDB)
async def create_new_tag_in_db(text: str, db: Session = Depends(get_db)) -> Tag:
    """
    Create new tag in db.

    Args:
        text (str):  Value.
        db (Session, optional):  The database session.
    Returns:
        Tag:  Database object Tag.
    """    
    return await create_tag_in_db(TagModel(text=text),db=db)


@router.get("/tag_id/{tag_id}", response_model=TagModel)
async def search_tag_by_id(tag_id: int, db: Session = Depends(get_db)) -> Tag | None:
    """
    Search ted by id.

    Args:
        tag_id (int):  Database object Tag id to search.
        db (Session, optional):  The database session.
    Raises:
        HTTPException:  HTTP_404_NOT_FOUND.
    Returns:
        Tag | None:  Database object Tag.
    """ 
    result = await get_tag_by_id(tag_id=tag_id, db=db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tag not found')
    return result


@router.post("/tags_by_string", response_model=list[TagDB])
async def create_tags_by_string(string: str, db: Session = Depends(get_db)) -> list[Tag]:
    """
    The method accepts a string and divides it by ",".
    Searches for or creates a new tag if one does not exist yet.

    _extended_summary_

    Args:
        string (str):  String with tags.
        db (Session, optional):  The database session.
    Returns:
        list[Tag]:  List[Database objects Tag]
    """    
    result = await get_list_of_tags_by_string(string=string, db=db)
    return result
