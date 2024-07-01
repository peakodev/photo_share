from sqlalchemy.orm import Session
from libgravatar import Gravatar

from app.models import User, Post, Comment
from app.schemas.user import UserModel, UserUpdateModel
from app.services.gravatar import get_gravatar


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    Get a user by email.

    :param email: The email of the user to get.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: The User, or None if the user does not exist.
    :rtype: User | None
    """
    return db.query(User).filter(User.email == email).first()


async def get_user_by_id(id: str, db: Session) -> User:
    """
    Get a user by id.

    :param id: The id of the user to get.
    :type id: str
    :param db: The database session.
    :type db: Session
    :return: User: The user, or None if the user does not exist.
    :rtype: User
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
                      first_name: str\n
                      last_name: str\n
                      email: str\n
                      password: str = Field(min_length=6, max_length=25)\n
                     }

    :param body: Schema
    :type body: UserModel
    :param db: The database session.
    :type db: Session
    :return: The created user.
    :rtype: User
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
                            first_name: str | None\n
                            last_name: str | None\n
                            email: str | None\n
                            avatar: str | None\n
                            }
    
    :param user_id: Database object User.id to update.
    :type user_id: int
    :param body: Schema.
    :type body: UserUpdateModel
    :param db: The database session.
    :type db: Session
    :return: Database object User.
    :rtype: User
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

    :param user: The user to update the token for.
    :type user: User
    :param token: The new token, or None to remove the token.
    :type token: str | None
    :param db: The database session.
    :type db: Session
    """    
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Confirm the email of a user.

    :param email: The email of the user to confirm.
    :type email: str
    :param db: The database session.
    :type db: Session
    """    
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email: str, url: str, db: Session) -> User:
    """
    Update the avatar of a user.

    :param email: The email of the user to update the avatar for.
    :type email: str
    :param url: The URL of the new avatar.
    :type url: str
    :param db: The database session.
    :type db: Session
    :return: The updated user.
    :rtype: User
    """    
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def update_password(user: User, password: str, db: Session) -> None:
    """
    Update the password of a user.

    :param user: The user to update the password for.
    :type user: User
    :param password: The new password.
    :type password: str
    :param db: The database session.
    :type db: Session
    """    
    user.password = password
    db.commit()
    db.refresh(user)


async def ban_user(user_id: int, is_ban: bool, db: Session) -> None:
    """
    Ban or unban a user.

    _extended_summary_

    :param user_id: The id of the user to ban or unban.
    :type user_id: int
    :param is_ban: True to ban the user, False to unban the user.
    :type is_ban: bool
    :param db: The database session.
    :type db: Session
    :rtype: None
    """    
    """
    Ban or unban a user.

    Args:
        user_id (int): The id of the user to ban or unban.
        is_ban (bool): True to ban the user, False to unban the user.
        db (Session): The database session.
    """
    user = db.query(User).filter_by(id=user_id).first()
    user.banned = is_ban
    db.commit()
    db.refresh(user)
    return user
