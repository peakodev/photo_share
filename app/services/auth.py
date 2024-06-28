from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session

from app.models import get_db
from app.repository import users as repository_users
from app.conf.config import settings


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password, hashed_password) -> bool:
        """
        Verify password

        Args:
            plain_password (_type_): The plain password
            hashed_password (bool): The hashed password

        Returns:
            bool: True if the password is correct, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Get password hash

        Args:
            password (str): The password

        Returns:
            str: The hashed password
        """
        return self.pwd_context.hash(password)

    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ) -> str:
        """
        Create a new access token

        Args:
            data (dict): JWT token data which should contain the user email
            expires_delta (Optional[float], optional): The expiration time in seconds. Defaults to None.

        Returns:
            str: The JWT token
        """
        return await self.__create_token(
            data, 150, scope="access_token", expires_delta=expires_delta
        )

    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ) -> str:
        """
        Create a new refresh token

        Args:
            data (dict): JWT token data which should contain the user email
            expires_delta (Optional[float], optional): The expiration time in seconds. Defaults to None.

        Returns:
            str: The JWT token
        """
        return await self.__create_token(
            data, 10080, scope="refresh_token", expires_delta=expires_delta
        )

    async def create_email_token(self, data: dict) -> str:
        """
        Create a new email token

        Args:
            data (dict): JWT token data which should contain the user email

        Returns:
            str: The JWT token
        """
        return await self.__create_token(data, 10080)

    async def __create_token(
        self,
        data: dict,
        default_delta: int,
        scope: Optional[str] = None,
        expires_delta: Optional[float] = None,
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(UTC) + timedelta(minutes=default_delta)
        to_encode.update({"iat": datetime.now(UTC), "exp": expire})
        if scope:
            to_encode.update({"scope": scope})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """
        Decode refresh token and return the email

        Args:
            refresh_token (str): The refresh token

        Raises:
            HTTPException: Raises an exception if invalid scope or credentials

        Returns:
            str: The email
        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
    ):
        """
        Get the current user from token

        Args:
            token (str, optional): The JWT token. Defaults to Depends(oauth2_scheme).
            db (Session, optional): The database session. Defaults to Depends(get_db).

        Raises:
            HTTPException: Raises an exeption when could not validate credentials

        Returns:
            User: The user
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            print(f"#S get_current_user --- start decode token")
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        print("#S get_current_user --- start get_user_by_email")
        user = await repository_users.get_user_by_email(email, db)
        print(f"#S get_current_user --- user: {user.email}")
        if user is None:
            raise credentials_exception
        if user.banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are banned from the system",
            )

        return user

    async def get_email_from_token(self, token: str) -> str:
        """
        Get email from token

        Args:
            token (str): The JWT token

        Raises:
            HTTPException: Raises an exception if invalid token for email verification

        Returns:
            str: The email
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )


auth_service = Auth()
