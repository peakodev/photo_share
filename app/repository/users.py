from sqlalchemy.orm import Session
from libgravatar import Gravatar

from app.models import User, Post, Comment
from app.schemas.user import UserModel, UserUpdateModel
from app.services.gravatar import get_gravatar


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    Get a user by email.

    Args:
        email (str):  The email of the user to get.
        db (Session):  The database session.
    Returns:
        User | None:  The User, or None if the user does not exist.
    """
    return db.query(User).filter(User.email == email).first()


async def get_user_by_id(id: str, db: Session) -> User:
    """
    Get a user by id.

    Args:
        id (str):  The id of the user to get.
        db (Session):  The database session.
    Returns:
        User:  The user, or None if the user does not exist.
    """    
    return db.query(User).filter(User.id == id).first()


async def user_posts_comments_number(user: User, db: Session) -> int:
    """
    Get the number of posts and comments for a user.
    """
    posts_number = db.query(Post).filter(Post.user_id == user.id).count()
    comments_number = db.query(Comment).filter(Comment.user_id == user.id).count()
    return posts_number, comments_number


async def create_user(body: UserModel, db: Session) -> User:
    """
    Create a new user.

    UserModel schema {
                      first_name: str,
                      last_name: str,
                      email: str,
                      password: str = Field(min_length=6, max_length=25)
                     }

    Args:
        body (UserModel):  Schema
        db (Session):  The database session.
    Returns:
        User:  The created user.
    """    
    avatar = None
    try:
        avatar = await get_gravatar(body.email)
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_user(user_id: int, body: UserUpdateModel, db: Session) -> User:
    """
    Update user parametrs.

    UserUpdateModel schema {
                            first_name: str | None,
                            last_name: str | None,
                            email: str | None,
                            avatar: str | None
                            }
    
    Args:
        user_id (int):  Database object User.id to update.
        body (UserUpdateModel):  Schema.
        db (Session):  The database session.
    Returns:
        User:  Database object User.
    """    
    user = db.query(User).filter_by(id=user_id).first()
    for key, value in body.model_dump(exclude_none=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Update the refresh token for a user.

    Args:
        user (User):  The user to update the token for.
        token (str | None):  The new token, or None to remove the token.
        db (Session):  The database session.
    """    
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Confirm the email of a user.

    Args:
        email (str):  The email of the user to confirm.
        db (Session):  The database session.
    """    
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email: str, url: str, db: Session) -> User:
    """
    Update the avatar of a user.

    Args:
        email (str):  The email of the user to update the avatar for.
        url (str):  The URL of the new avatar.
        db (Session):  The database session.
    Returns:
        User:  The updated user.
    """    
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def update_password(user: User, password: str, db: Session) -> None:
    """
    Update the password of a user.

    Args:
        user (User):  The user to update the password for.
        password (str):  The new password.
        db (Session):  The database session.

    """    
    user.password = password
    db.commit()
    db.refresh(user)


async def ban_user(user_id: int, is_ban: bool, db: Session) -> None:
    """
    Ban or unban a user.

    Args:
        user_id (int): The id of the user to ban or unban.
        is_ban (bool): True to ban the user, False to unban the user.
        db (Session): The database session.    Args:
        user_id (int):  The id of the user to ban or unban.
        is_ban (bool):  True to ban the user, False to unban the user.
        db (Session):  The database session.
        None: 
    """
    user = db.query(User).filter_by(id=user_id).first()
    user.banned = is_ban
    db.commit()
    db.refresh(user)
    return user
