import unittest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from sqlalchemy.orm import Session

from app.repository import comments
from app.models import Comment, User
from app.schemas.comments import CommentCreate, CommentUpdate


class TestCommentsRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=Session)
        self.user = User(
            id=1,
            first_name="Adam",
            last_name="Kovalski",
            email="adamkovalski@test.com",
            password="Hardpassword",
            created_at=datetime.now(),
            refresh_token="test",
            avatar=None,
            confirmed=True,
        )
        self.test_comment = Comment(
            id=1,
            text="Test comment",
            created_at=datetime.now(),
            updated_at=None,
            user_id=1,
            user=self.user,
            post_id=1,
        )

    async def test_get_comment_by_id(self):
        self.session.execute.return_value.scalar_one_or_none = MagicMock(return_value=self.test_comment)

        result = await comments.get_comment_by_id(self.test_comment.id, self.session)

        self.assertIsNotNone(result)
        self.assertEqual(result, self.test_comment)

    async def test_get_comments_by_post(self):
        post_id = 1
        offset = 0
        limit = 10
        comment_list = [Comment(id=i, text=f"Test comment {i}") for i in range(1, 11)]
        self.session.execute.return_value.scalars.return_value.all = MagicMock(return_value=comment_list)

        result = await comments.get_comments_by_post(post_id, offset, limit, self.session)
        print(result)
        self.assertEqual(result, comment_list)

    async def test_create_comment(self):
        comment_data = CommentCreate(text="New comment", post_id=1)
        db_comment = Comment(id=1, text="New comment", post_id=1, user_id=1)
        self.session.add = AsyncMock()
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()

        result = await comments.create_comment(comment_data, self.user.id, self.session)
        self.assertEqual(result.text, comment_data.text)
        self.assertEqual(result.user_id, self.user.id)

    async def test_update_comment(self):
        comment_id = 1
        update_data = CommentUpdate(text="Updated comment")
        db_comment = Comment(id=comment_id, text="Old comment")
        self.session.query().filter_by().first.return_value = db_comment
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()

        result = await comments.update_comment(comment_id, update_data, self.session)
        self.assertEqual(result.text, update_data.text)

    async def test_delete_comment(self):
        comment_id = 1
        db_comment = Comment(id=comment_id, text="Test comment")
        self.session.query().filter_by().first.return_value = db_comment
        self.session.delete = AsyncMock()
        self.session.commit = AsyncMock()

        result = await comments.delete_comment(comment_id, self.session)
        self.assertEqual(result, db_comment)


if __name__ == '__main__':
    unittest.main()
