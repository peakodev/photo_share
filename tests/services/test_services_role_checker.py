import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.models import Role, User
from app.services.auth import auth_service
from app.services.role_checker import moderator_required, admin_required


class TestRoleRequired(unittest.TestCase):

    @patch('app.services.auth.auth_service.get_current_user')
    def test_moderator_required_with_moderator(self, mock_get_current_user):
        mock_user = MagicMock(spec=User)
        mock_user.role = Role.moderator
        mock_get_current_user.return_value = mock_user

        # Call the dependency directly
        result = moderator_required(mock_user)
        self.assertEqual(result, mock_user)

    @patch('app.services.auth.auth_service.get_current_user')
    def test_moderator_required_with_non_moderator(self, mock_get_current_user):
        mock_user = MagicMock(spec=User)
        mock_user.role = Role.user
        mock_get_current_user.return_value = mock_user

        # Expect an HTTPException to be raised
        with self.assertRaises(HTTPException) as context:
            moderator_required(mock_user)
        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.detail, "Insufficient permissions")

    @patch('app.services.auth.auth_service.get_current_user')
    def test_admin_required_with_admin(self, mock_get_current_user):
        mock_user = MagicMock(spec=User)
        mock_user.role = Role.admin
        mock_get_current_user.return_value = mock_user

        # Call the dependency directly
        result = admin_required(mock_user)
        self.assertEqual(result, mock_user)

    @patch('app.services.auth.auth_service.get_current_user')
    def test_admin_required_with_non_admin(self, mock_get_current_user):
        mock_user = MagicMock(spec=User)
        mock_user.role = Role.user
        mock_get_current_user.return_value = mock_user

        # Expect an HTTPException to be raised
        with self.assertRaises(HTTPException) as context:
            admin_required(mock_user)
        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.detail, "Insufficient permissions")


if __name__ == '__main__':
    unittest.main()
