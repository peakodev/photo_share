import pytest
from unittest.mock import AsyncMock, patch

from app.services.email import send_email, send_reset_password_email
from fastapi_mail.errors import ConnectionErrors


@pytest.mark.asyncio
@patch('app.services.email.auth_service.create_email_token', new_callable=AsyncMock)
@patch('app.services.email.FastMail')
async def test_send_email(mock_fastmail, mock_create_email_token):
    # Arrange
    email = 'test@example.com'
    host = 'http://testserver'
    mock_create_email_token.return_value = 'mocked_token'
    mock_fastmail_instance = mock_fastmail.return_value
    mock_fastmail_instance.send_message = AsyncMock()

    # Act
    await send_email(email, host)

    # Assert
    mock_create_email_token.assert_awaited_once_with({"sub": email})
    mock_fastmail_instance.send_message.assert_awaited_once()
    message = mock_fastmail_instance.send_message.call_args[0][0]
    assert message.subject == 'Confirm your email address'
    assert message.recipients == [email]
    assert message.template_body['token'] == 'mocked_token'


@pytest.mark.asyncio
@patch('app.services.email.auth_service.create_email_token', new_callable=AsyncMock)
@patch('app.services.email.FastMail')
async def test_send_reset_password_email(mock_fastmail, mock_create_email_token):
    # Arrange
    email = 'test@example.com'
    host = 'http://testserver'
    mock_create_email_token.return_value = 'mocked_token'
    mock_fastmail_instance = mock_fastmail.return_value
    mock_fastmail_instance.send_message = AsyncMock()

    # Act
    await send_reset_password_email(email, host)

    # Assert
    mock_create_email_token.assert_awaited_once_with({"sub": email})
    mock_fastmail_instance.send_message.assert_awaited_once()
    message = mock_fastmail_instance.send_message.call_args[0][0]
    assert message.subject == 'Reset your password'
    assert message.recipients == [email]
    assert message.template_body['token'] == 'mocked_token'


@pytest.mark.asyncio
@patch('app.services.email.auth_service.create_email_token', new_callable=AsyncMock)
@patch('app.services.email.FastMail')
async def test_send_email_connection_error(mock_fastmail, mock_create_email_token):
    # Arrange
    email = 'test@example.com'
    host = 'http://testserver'
    mock_create_email_token.return_value = 'mocked_token'
    mock_fastmail_instance = mock_fastmail.return_value
    mock_fastmail_instance.send_message = AsyncMock(side_effect=ConnectionErrors('Connection error'))

    # Act & Assert
    with pytest.raises(ConnectionErrors):
        await send_email(email, host)


@pytest.mark.asyncio
@patch('app.services.email.auth_service.create_email_token', new_callable=AsyncMock)
@patch('app.services.email.FastMail')
async def test_send_reset_password_email_connection_error(mock_fastmail, mock_create_email_token):
    # Arrange
    email = 'test@example.com'
    host = 'http://testserver'
    mock_create_email_token.return_value = 'mocked_token'
    mock_fastmail_instance = mock_fastmail.return_value
    mock_fastmail_instance.send_message = AsyncMock(side_effect=ConnectionErrors('Connection error'))

    # Act & Assert
    with pytest.raises(ConnectionErrors):
        await send_reset_password_email(email, host)
