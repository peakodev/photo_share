from fastapi import (
    APIRouter,
    Depends,
    status,
    Security,
    Request,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from app.database.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    request: Request,
    db: Session = Depends(get_db)
):
    # TODO
    return {"user": {'id': 1}, "detail": "User successfully created"}


@router.post("/login")
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # TODO
    return {
        "access_token": None,
        "refresh_token": None,
        "token_type": "bearer",
    }


@router.get("/refresh_token")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    # TODO
    return {
        "access_token": None,
        "refresh_token": None,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(
    token: str,
    db: Session = Depends(get_db)
):
    # TODO
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    request: Request,
    db: Session = Depends(get_db),
):
    # TODO
    return {"message": "Check your email for confirmation."}


@router.post("/forgot_password")
async def forgot_password(
    request: Request,
    db: Session = Depends(get_db),
):
    # TODO
    return {"message": "Check your email for password reset link."}


@router.post("/reset_password/{token}")
async def reset_password(
    token: str,
    db: Session = Depends(get_db),
):
    # TODO
    return {"message": "Password successfully changed"}
