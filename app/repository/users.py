from libgravatar import Gravatar
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Get a user by email.

    Args:
        email (str): The email of the user to get.
        db (Session): The database session.

    Returns:
        User: The user, or None if the user does not exist.
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Create a new user.

    Args:
        body (UserModel): The user data.
        db (Session): The database session.

    Returns:
        User: The created user.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Update the refresh token for a user.

    Args:
        user (User): The user to update the token for.
        token (str | None): The new token, or None to remove the token.
        db (Session): The database session.
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Confirm the email of a user.

    Args:
        email (str): The email of the user to confirm.
        db (Session): The database session.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email: str, url: str, db: Session) -> User:
    """
    Update the avatar of a user.

    Args:
        email (str): The email of the user to update the avatar for.
        url (str): The URL of the new avatar.
        db (Session): The database session.

    Returns:
        User: The updated user.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def update_password(user: User, password: str, db: Session) -> None:
    """
    Update the password of a user.

    Args:
        user (User): The user to update the password for.
        password (str): The new password.
        db (Session): The database session.
    """
    user.password = password
    db.commit()
    db.refresh(user)
