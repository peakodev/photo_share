from os import getcwd
import sys
sys.path.insert(1, getcwd())
from datetime import datetime, timedelta

import unittest
from sqlalchemy.orm import Session
from unittest.mock import AsyncMock, MagicMock
from fastapi import UploadFile

from app.models.comment import Comment
from app.models.user import User
from app.models.tag import Tag
from app.models.post import Post
from app.repository.posts import (create_post,
                                  find_posts,
                                  get_post,
                                  get_all_posts,
                                  get_posts,
                                  update_post,
                                  delete_post)

counter = 1

class TestPostReposetory(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=Session)
        self.user = User(
                        id=1,
                        first_name="Adam",
                        last_name="Kovalski",
                        email="adamkovalski@test.com",
                        password="Hardpassword",
                        created_at= datetime.now(),
                        refresh_token="test",
                        avatar=None,
                        confirmed=True,
                        )
        self.test_post = Post(id=1,
                      photo_url="test_url_1",
                      photo_public_id="test_url_2",
                      transform_url="test_url_3",
                      description="test_description_1",
                      created_at=datetime.now(),
                      updated_at=None,
                      tags = [Tag(id=1, text="test_tag")],
                      rating = 5,
                      user_id = 1,
                      user = self.user
                      )
        global counter
        print(f"Test №{counter} started")
        
    def tearDown(self):
        global counter
        print(f"Test №{counter} finished")
        counter += 1


    async def test_create_post_with_valid_values_found(self):
        """
        Test for function: app.repository.posts.create_post()
        """
        test_file = UploadFile
        with open(f"{getcwd()}\\tests\\user-default.png","rb") as file:
            test_file = UploadFile(file.read())
        result = await create_post(description="test seccess",
                                   tags="test, new, help",
                                   file=test_file,
                                   user=self.user,
                                   db=self.session)
        
        self.assertIsInstance(result, Post)
        self.assertEqual(result.description, "test seccess")

    async def test_create_post_without_tags(self):
        test_file = UploadFile
        with open(f"{getcwd()}\\tests\\user-default.png","rb") as file:
            test_file = UploadFile(file.read())
        result = await create_post(description="test seccess",
                                   tags="",
                                   file=test_file,
                                   user=self.user,
                                   db=self.session)
        
        self.assertIsInstance(result, Post)
        self.assertEqual(result.description, "test seccess")
        self.assertEqual(result.tags, [])

    async def test_update_post_description_found(self):
        """
        Test for function: app.repository.posts.update_post()
        Update description
        """ 
        new_description = "Seccess"
        post = Post()
        self.session.query().filter_by().first.return_value = post
        self.session.commit.return_value = post
        result = await update_post(post_id=1,
                                   user=self.user,
                                   db=self.session,
                                   description=new_description)
        self.assertIsInstance(result, Post)
        self.assertEqual(result.description, new_description)
        self.assertEqual(datetime, type(result.updated_at))

    async def test_update_post_tags_found(self):
        """
        Test for function: app.repository.posts.update_post()
        Update tags
        """ 
        new_tags = 'test1,test2,test3'
        post = self.test_post
        self.session.query().filter_by().first.return_value = post
        result = await update_post(post_id=1,
                                   user=self.user,
                                   db=self.session,
                                   tags=new_tags)
        self.assertIsInstance(result, Post)
        self.assertEqual(3, len(result.tags))
        self.assertEqual(datetime, type(result.updated_at))
    
    async def test_update_post_file_found(self):
        """
        Test for function: app.repository.posts.update_post()
        Update picture
        """ 
        test_file = UploadFile
        with open(f"{getcwd()}\\tests\\user-default.png","rb") as file:
            test_file = UploadFile(file.read())
        post = self.test_post
        self.session.query().filter_by().first.return_value = post
        result = await update_post(post_id=1,
                                    user=self.user,
                                    db=self.session,
                                    file=test_file)
        self.assertIsInstance(result, Post)
        self.assertEqual(datetime, type(result.updated_at))

    
    async def test_update_post_file_not_found(self):
        """
        Test for function: app.repository.posts.update_post()
        Update picture
        """ 
        test_file = "string for fail"
        post = self.test_post
        self.session.query().filter_by().first.return_value = post
        with self.assertRaises(AttributeError):
            await update_post(post_id=1,
                                user=self.user,
                                db=self.session,
                                file=test_file)


    
    async def test_find_posts_by_text_in_discription(self):
        """
        Test for function: app.repository.posts.find_posts()
        """        
        posts = [Post,Post,Post]
        self.session.query().filter().all.return_value = posts
        result = await find_posts(find_str="test", user=self.user, db=self.session)
        self.assertEqual(result, posts)

    async def test_get_post_by_id(self):
        """
        Test for function: app.repository.posts.get_post()
        """ 
        post = Post()
        self.session.query().filter_by().first.return_value = post
        result = await get_post(post_id=1, user=self.user, db=self.session)
        self.assertEqual(result, post)

    async def test_get_all_posts_of_all_users(self):
        """
        Test for function: app.repository.posts.get_all_posts()
        """ 
        posts = [Post, Post, Post]
        self.session.query().offset().limit().all.return_value = posts
        result = await get_all_posts(limit=10, offset=1, db=self.session)
        self.assertEqual(result, posts)

    async def test_get_posts_for_curent_user(self):
        """
        Test for function: app.repository.posts.get_posts()
        """ 
        posts = [self.test_post,
                 Post(id=2,
                      photo_url="test_url_4",
                      photo_public_id="test_url_5",
                      transform_url="test_url_6",
                      description="test_description_2",
                      created_at=datetime.now(),
                      updated_at=None,
                      tags = [Tag(id=1, text="test")],
                      rating = 5,
                      user_id = 1,
                      user = self.user
                      ), 
                 Post(id=3,
                      photo_url="test_url_7",
                      photo_public_id="test_url_8",
                      transform_url="test_url_9",
                      description="test_description",
                      created_at=datetime.now(),
                      updated_at=None,
                      tags = [Tag(id=1, text="test")],
                      rating = 5,
                      user_id = 1,
                      user = self.user
                      )]
        self.session.query().filter_by().offset().limit().all.return_value = posts
        result = await get_posts(limit=5, offset=0, user=self.user, db=self.session)
        self.assertEqual(result, posts)



if __name__ == "__main__":
    unittest.main()