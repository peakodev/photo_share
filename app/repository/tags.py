from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database.tag import Tag
from app.database.post import Post
from app.schemas.tags import TagModel


async def get_tags(db: Session, skip: int = 0, limit: int = 100) -> List[Tag]:
    """
    Get all tags from db.

    Args:
        skip (int): skip
        limit (int): limit
        db (Session): The database session.

    Returns:
        List[Tag]: List of all tags.
    """    
    return db.query(Tag).offset(skip).limit(limit).all()

async def create_tag_in_db(body: TagModel, db: Session) -> Tag:
    """
    Create a new tag in db.

    Args:
        body (TagModel): TagModel model: {tag: str}
        db (Session): The database session.

    Returns:
        Tag: Database object.
    """    
    _tag = Tag(text=body.text)
    db.add(_tag)
    db.commit()
    db.refresh(_tag)
    return _tag
    
async def get_tag_by_id(tag_id: int, db: Session) -> Tag | None:
    """
    Search database object Tag by id.

    Args:
        tag_id (int): id of tag
        db (Session): The database session.

    Returns:
        Tag | None: Database object
    """    
    return db.query(Tag).filter(Tag.id == tag_id).first()

async def get_tag_by_text(text: str, db: Session) -> Tag | None:
    """
    Search database object Tag by text.

    Args:
        text (str): tag value
        db (Session): The database session.

    Returns:
        Tag | None: Database object
    """    
    return db.query(Tag).filter(Tag.text == text).first()

async def get_list_of_tags_by_string(string: str, db: Session) -> list[int]:
    """
    The function accepts a string and divides it by ",".

    Searches for or creates a new tag if one does not exist yet.

    Args:
        string (str): string with tags
        db (Session): The database session.
        
    Returns:
        list[int] : Returns a list of id's tags
    """    
    tag_list = string.split(",")
    result = []
    for item in tag_list:
        new_tag = await get_tag_by_text(item.strip().lower(), db=db)
        if new_tag:
            result.append(new_tag.id)
        else:
            new_tag = await create_tag_in_db(TagModel(text = item.lower().strip()), db=db)
            result.append(new_tag.id)
        if len(result) == 5:
            break
    return result

