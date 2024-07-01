from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import Tag, Post
from app.schemas.tags import TagModel


async def get_tags(db: Session, skip: int = 0, limit: int = 100) -> List[Tag]:
    """
    Get all tags.

    :param db: The database session.
    :type db: Session
    :param skip: Skip, defaults to 0.
    :type skip: int, optional
    :param limit: Limit, defaults to 100.
    :type limit: int, optional
    :return: List[Database objects Tag]
    :rtype: List[Tag]
    """    
    return db.query(Tag).offset(skip).limit(limit).all()


async def create_tag_in_db(body: TagModel, db: Session) -> Tag:
    """
    Create tag in db.

    TagModel schema {tag: str}

    :param body: Schema.
    :type body: TagModel
    :param db: The database session.
    :type db: Session
    :return: Database object Tag.
    :rtype: Tag
    """    
    _tag = Tag(text=body.text)
    db.add(_tag)
    db.commit()
    db.refresh(_tag)
    return _tag


async def get_tag_by_id(tag_id: int, db: Session) -> Tag | None:
    """
    Get tag by id.

    :param tag_id: Database object Tag id to search.
    :type tag_id: int
    :param db: The database session.
    :type db: Session
    :return: Database object Tag.
    :rtype: Tag | None
    """    
    return db.query(Tag).filter(Tag.id == tag_id).first()


async def get_tag_by_text(text: str, db: Session) -> Tag | None:
    """
    Search database object Tag by text.

    :param text: Database object Tag.text to search.
    :type text: str
    :param db: The database session.
    :type db: Session
    :return: Database object Tag.
    :rtype: Tag | None
    """    
    return db.query(Tag).filter(Tag.text == text).first()


async def get_list_of_tags_by_string(string: str | None, db: Session) -> list[Tag]:
    """
    The function accepts a string and divides it by ",".

    Searches for or creates a new tag if one does not exist yet.

    :param string: String with tags.
    :type string: str | None
    :param db: The database session.
    :type db: Session
    :return: List[Database objects Tag]
    :rtype: list[Tag]
    """    
    if not string:
        return []
    tag_list = string.split(",")
    result = []
    for item in tag_list:
        item = item.strip().lower()
        if item == '':
            continue
        new_tag = await get_tag_by_text(item, db=db)
        if new_tag:
            result.append(new_tag)
        else:
            new_tag = await create_tag_in_db(TagModel(text=item), db=db)
            result.append(new_tag)
        if len(result) == 5:
            break
    return result


async def search_tags_by_query(query: str, db: Session) -> List[Tag]:
    """
    Search tags by query.

    _extended_summary_

    :param query: Search query.
    :type query: str
    :param db: The database session.
    :type db: Session
    :return: List[Database objects Tag]
    :rtype: List[Tag]
    """    
    return db.query(Tag).filter(Tag.text.ilike(f"%{query}%")).all()


async def get_tags_by_name(tags: List[str], db: Session) -> List[Tag]:
    """
    Search tags by name.

    :param tags: List of tags
    :type tags: List[str]
    :param db: The database session.
    :type db: Session
    :return: List[Database objects Tag]
    :rtype: List[Tag]
    """    
    return db.query(Tag).filter(Tag.text.in_(tags)).all()
