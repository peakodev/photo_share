from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from app.services.auth import auth_service
from app.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="PhotoShare Application",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=settings.mail_validate_cert,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, host: str):
    """
    Send email to user

    Args:
        email (EmailStr): The email of the user to send the email to.
        host (str): The host of the application.
    """
    try:
        token_verification = await auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email address",
            recipients=[email],
            template_body={
                "subject": "Email confirmation",
                "host": host,
                "username": email,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)
        raise ConnectionErrors(err)


async def send_reset_password_email(email: EmailStr, host: str):
    """
    Send email to user to reset password

    Args:
        email (EmailStr): The email of the user to send the email to.
        host (str): The host of the application.
    """
    try:
        token_verification = await auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Reset your password",
            recipients=[email],
            template_body={
                "subject": "Reset password",
                "host": host,
                "username": email,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_reset_passwd_template.html")
    except ConnectionErrors as err:
        print(err)
        raise ConnectionErrors(err)