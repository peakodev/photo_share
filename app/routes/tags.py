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

    :param db: The database session
    :type db: Session, optional
    :return: List of Database objects Tag
    :rtype: list[Tag]
    """    
    return await get_tags(db=db)


@router.get("/tag_value/{text}",response_model=TagDB)
async def search_tag_by_text(text:str, db: Session = Depends(get_db)) -> Tag | None:
    """
    Search tag in db by value.

    :param text: Text for search.
    :type text: str
    :param db: The database session.
    :type db: Session, optional
    :raises HTTPException: HTTP_404_NOT_FOUND
    :return: Database object Tag
    :rtype: Tag | None
    """    
    result = await get_tag_by_text(text=text, db=db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tag not found')
    return result


@router.post("", response_model=TagDB)
async def create_new_tag_in_db(text: str, db: Session = Depends(get_db)) -> Tag:
    """
    Create new tag in db.

    :param text: Value.
    :type text: str
    :param db: The database session.
    :type db: Session, optional
    :return: Database object Tag.
    :rtype: Tag
    """    
    return await create_tag_in_db(TagModel(text=text),db=db)


@router.get("/tag_id/{tag_id}", response_model=TagModel)
async def search_tag_by_id(tag_id: int, db: Session = Depends(get_db)) -> Tag | None:
    """
    Search ted by id.

    :param tag_id: Database object Tag id to search.
    :type tag_id: int
    :param db: The database session.
    :type db: Session, optional
    :raises HTTPException: HTTP_404_NOT_FOUND
    :return: Database object Tag.
    :rtype: Tag | None
    """    
    """
    Search ted by id.
    Args:
        tag_id (int): tag id
        db (Session, optional): The database session. Defaults to Depends(get_db).
    Raises:
        HTTPException: HTTP_404_NOT_FOUND
    Returns:
        Tag | None: Database object.
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

    :param string: String with tags.
    :type string: str
    :param db: The database session
    :type db: Session, optional
    :return: List[Database objects Tag]
    :rtype: list[Tag]
    """    
    result = await get_list_of_tags_by_string(string=string, db=db)
    return result
