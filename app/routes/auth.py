from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from app.models import get_db
from app.schemas.user import UserModel, UserResponse, TokenModel, RequestEmail, ResetPasswordModel
from app.repository import users as repository_users
from app.services.auth import auth_service
from app.services.email import send_email, send_reset_password_email

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post(
    "/signup",
    response_model=UserResponse,
    name="auth_post_signup",
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Signup user.

    UserModel schema {
                      first_name: str\n
                      last_name: str\n
                      email: str\n
                      password: str = Field(min_length=6, max_length=25)\n
                      }

    :param body: Schema
    :type body: UserModel
    :param background_tasks: BackgroundTasks
    :type background_tasks: BackgroundTasks
    :param request: Request
    :type request: Request
    :param db: The database session.
    :type db: Session, optional
    :raises HTTPException: HTTP_409_CONFLICT
    :return: massage
    :rtype: json
    """
    print(f"#b_R - body.email: {body.email}")
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, request.base_url)
    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login", name="auth_signin", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Login user.

    :param body: Form
    :type body: OAuth2PasswordRequestForm, optional
    :param db: The database session.
    :type db: Session, optional
    :raises HTTPException: HTTP_401_UNAUTHORIZED
    :raises HTTPException: HTTP_404_NOT_FOUND
    :return: JWT Tokens
    :rtype: json
    """
    print(f"#R_Login - verifying email: {body.username}")
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )
    if user.banned:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are banned. Please concact admin"
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", name="refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """
    Refresh token.

    :param credentials: Security
    :type credentials: HTTPAuthorizationCredentials, optional
    :param db: The database session.
    :type db: Session, optional
    :raises HTTPException: HTTP_401_UNAUTHORIZED
    :return: JWT Tokens
    :rtype: json
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.banned:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are banned. Please concact admin"
        )
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get(
    "/confirm_email/{token}",
    name="confirm_email",
)
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirmed email.

    :param token: Email token
    :type token: str
    :param db: The database session.
    :type db: Session, optional
    :raises HTTPException: HTTP_400_BAD_REQUEST
    :return: Massage
    :rtype: json
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/resend_confirm_email", name="resend_confirm_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Request email.

    RequestEmail schema {
                        email: EmailStr\n
                        }

    :param body: Schema
    :type body: RequestEmail
    :param background_tasks: BackgroundTasks
    :type background_tasks: BackgroundTasks
    :param request: Request
    :type request: Request
    :param db: The database session.
    :type db: Session, optional
    :raises HTTPException: HTTP_404_NOT_FOUND
    :return: Massage
    :rtype: json
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid email"
        )

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, request.base_url)
    return {"message": "Check your email for confirmation."}


@router.post("/forgot_password")
async def forgot_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Forgot password

    RequestEmail schema {
                        email: EmailStr\n
                        }

    :param body: Schema
    :type body: RequestEmail
    :param background_tasks: BackgroundTasks
    :type background_tasks: BackgroundTasks
    :param request: Request
    :type request: Request
    :param db: The database session.
    :type db: Session, optional
    :raises HTTPException: HTTP_404_NOT_FOUND
    :return: Massage
    :rtype: json
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email not found"
        )

    auth_service.create_email_token(user.email)
    background_tasks.add_task(send_reset_password_email, user.email, request.base_url)

    return {"message": "Check your email for password reset link."}


@router.post("/reset_password")
async def reset_password(
    body: ResetPasswordModel,
    db: Session = Depends(get_db),
):

    """
    Reset password.

    ResetPasswordModel schema {
                      token: str\n
                      password: str = Field(min_length=6, max_length=25)\n
                      }

    :param body: Schema
    :type body: UserModel
    :param db: The database session.
    :type db: Session, optional
    :raises HTTPException: HTTP_404_NOT_FOUND
    :return: Massage
    :rtype: json
    """
    email = await auth_service.get_email_from_token(body.token)
    user = await repository_users.get_user_by_email(email, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reset password error"
        )

    await repository_users.update_password(
        user, auth_service.get_password_hash(body.password), db
    )

    return {"message": "Password successfully changed"}
