import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.orm import Session

from app.models import Post, User
from app.services.rating import add_rate_to_post, calculate_avarage_rating


class TestRatingService(unittest.IsolatedAsyncioTestCase):
    
    @patch('app.services.rating.calculate_avarage_rating', new_callable=AsyncMock)
    async def test_add_rate_to_post(self, mock_calculate_avarage_rating):
        # Create mock objects for user, post, and db session
        mock_user = User(id=1)
        mock_post = Post(id=1, rating=0)
        mock_db = MagicMock(spec=Session)
        
        # Set the mock for calculate_avarage_rating
        mock_calculate_avarage_rating.return_value = 4.5

        # Call the function with the mock objects
        response = await add_rate_to_post(mock_user, mock_post, 4, mock_db)
        
        # Check if the function returns the expected result
        self.assertEqual(response, {"post_id": mock_post.id, "rating": 4.5})

        # Verify that db.add, db.commit, and db.refresh were called
        self.assertTrue(mock_db.add.called)
        self.assertTrue(mock_db.commit.called)
        self.assertTrue(mock_db.refresh.called)

    async def test_calculate_avarage_rating(self):
        # Create mock objects for post and db session
        mock_post = Post(id=1, rating=0)
        mock_db = MagicMock(spec=Session)
        
        # Set the return value for the query
        mock_db.query().filter().first.return_value = MagicMock(average_rate=4.5)
        
        # Call the function with the mock objects
        rating = await calculate_avarage_rating(mock_post, mock_db)
        
        # Check if the function returns the expected result
        self.assertEqual(rating, 4.5)

        # Verify that db.add, db.commit, and db.refresh were called
        self.assertTrue(mock_db.add.called)
        self.assertTrue(mock_db.commit.called)
        self.assertTrue(mock_db.refresh.called)


if __name__ == "__main__":
    unittest.main()
