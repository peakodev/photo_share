from os import getcwd
from pathlib import Path
import sys
sys.path.insert(1, getcwd())
from datetime import datetime, timedelta
from urllib.request import urlopen

import unittest
from sqlalchemy.orm import Session
from unittest.mock import AsyncMock
from fastapi import UploadFile

from app.models.post import Post
from app.models.tag import Tag
from app.repository.admin import delete_post_by_id, update_post_by_id


class TestPostReposetory(unittest.IsolatedAsyncioTestCase):

    file_path = Path(getcwd()) / "tests" / "user-default.png"

    def setUp(self):
        self.session = AsyncMock(spec=Session)
        
    async def test_delete_post_by_id_post_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await delete_post_by_id(post_id=1, db=self.session)
        self.assertEqual(result, None)

    async def test_delete_post_by_id_post_found(self):
        post = Post(id=1)
        self.session.query().filter_by().first.return_value = post
        result = await delete_post_by_id(post_id=1, db=self.session)
        self.assertIsInstance(result, Post)
        self.assertEqual(result.id, 1)

    async def test_update_post_by_id_update_photo_post_found(self):
        test_file = UploadFile
        with self.file_path.open("rb") as file:
            binary_string = file.read()
            test_file = UploadFile(binary_string)
        self.session.query().filter_by().first.return_value = Post(id=1,
                                                                   photo_url='',
                                                                   photo_public_id=''
                                                                   )
        result = await update_post_by_id(post_id=1, db=self.session, photo=test_file)
        self.assertIsInstance(result, Post)
        print(result.photo_url)
        photo_by_url = urlopen(result.photo_url).read()
        self.assertEqual(photo_by_url, binary_string)
    
    async def test_update_post_by_id_update_photo_post_not_found(self):
        test_file = UploadFile
        with self.file_path.open("rb") as file:
            binary_string = file.read()
            test_file = UploadFile(binary_string)
        self.session.query().filter_by().first.return_value = None
        result = await update_post_by_id(post_id=1, db=self.session, photo=test_file)
        self.assertEqual(result, None)

    async def test_update_post_by_id_update_description_post_found(self):
        new_description = "new description"
        self.session.query().filter_by().first.return_value = Post(id=1,
                                                                   description="test discription")

        result = await update_post_by_id(post_id=1, db=self.session, description=new_description)
        self.assertIsInstance(result, Post)
        self.assertEqual(result.description, new_description)

    async def test_update_post_by_id_update_rating_post_found(self):
        new_rating = 4
        self.session.query().filter_by().first.return_value = Post(id=1,
                                                                   rating=1)
        result = await update_post_by_id(post_id=1, db=self.session, rating=new_rating)
        self.assertIsInstance(result, Post)
        self.assertEqual(result.rating, new_rating)


if __name__ == "__main__":
    unittest.main()
