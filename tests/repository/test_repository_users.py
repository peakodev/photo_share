import unittest
from unittest.mock import MagicMock, patch
from libgravatar import Gravatar
from sqlalchemy.orm import Session
from app.models import User
from app.schemas.user import UserModel
from app.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
    update_password,
    ban_user
)


class TestUserRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db = MagicMock(spec=Session)
        self.user = User(id=1, first_name="nazar", last_name="test", banned=False,
                         email="test@example.com", password="hashedpassword", confirmed=False)
        self.user_data = UserModel(first_name="nazar", last_name="test",
                                   email="test@example.com", password="hashedpassword")

    async def test_get_user_by_email(self):
        self.db.query.return_value.filter.return_value.first.return_value = self.user

        result = await get_user_by_email(self.user.email, self.db)

        self.assertEqual(result, self.user)
        self.db.query.assert_called_once_with(User)
        filter_call_args = self.db.query.return_value.filter.call_args[0][0]
        self.assertEqual(str(filter_call_args), str(User.email == self.user.email))

    @patch.object(Gravatar, 'get_image', return_value="avatar_url")
    async def test_create_user(self, mock_get_image):
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = None

        result = await create_user(self.user_data, self.db)

        self.assertEqual(result.email, self.user_data.email)
        self.assertEqual(result.avatar, "avatar_url")
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once()

    async def test_update_token(self):
        token = "new_token"

        await update_token(self.user, token, self.db)

        self.assertEqual(self.user.refresh_token, token)
        self.db.commit.assert_called_once()

    async def test_confirmed_email(self):
        self.db.query.return_value.filter.return_value.first.return_value = self.user

        await confirmed_email(self.user.email, self.db)

        self.assertTrue(self.user.confirmed)
        self.db.commit.assert_called_once()

    async def test_update_avatar(self):
        self.db.query.return_value.filter.return_value.first.return_value = self.user
        new_avatar_url = "new_avatar_url"

        result = await update_avatar(self.user.email, new_avatar_url, self.db)

        self.assertEqual(result.avatar, new_avatar_url)
        self.db.commit.assert_called_once()

    async def test_update_password(self):
        new_password = "new_password"

        await update_password(self.user, new_password, self.db)

        self.assertEqual(self.user.password, new_password)
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(self.user)

    async def test_ban_user(self):
        self.db.query.return_value.filter.return_value.first.return_value = self.user

        res_user = await ban_user(self.user.id, True, self.db)

        self.assertEqual(res_user.banned, True)
        self.db.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
