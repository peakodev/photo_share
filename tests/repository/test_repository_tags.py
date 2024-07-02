from os import getcwd
import sys
sys.path.insert(1, getcwd())
from datetime import datetime, timedelta

import unittest
from sqlalchemy.orm import Session
from unittest.mock import AsyncMock, MagicMock

from app.models.tag import Tag
from app.schemas.tags import TagModel
from app.repository.tags import (get_list_of_tags_by_string,
                                 get_tag_by_id,
                                 get_tag_by_text,
                                 get_tags,
                                 create_tag_in_db)


class TestTagsRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=Session)
        
    async def test_create_tag_in_db(self):
        """
        Test for function: app.repository.tags.create_tag_in_db()
        """        
        test_model = TagModel(text="test_text")
        result = await create_tag_in_db(body=test_model, db=self.session)
        self.assertIsInstance(result, Tag)
        self.assertEqual(result.text, test_model.text)

    async def test_one_get_list_of_tag_by_string(self):
        """
        Test for function: app.repository.tags.get_list_of_tag_by_string()
        Сhecking whether 5 tag models will be created
        """    
        test_string = "new, test, tag, help, ok, nok"
        expected_result = [
            Tag(id=1, text="new"),
            Tag(id=2, text="test"),
            Tag(id=3, text="tag"),
            Tag(id=4, text="help"),
            Tag(id=5, text="ok")
        ]
        self.session.query().filter().first.return_value = None
        result = await get_list_of_tags_by_string(test_string, self.session)
        self.assertEqual(result[0].text, expected_result[0].text)
        self.assertEqual(result[1].text, expected_result[1].text)
        self.assertEqual(result[2].text, expected_result[2].text)
        self.assertEqual(result[3].text, expected_result[3].text)
        self.assertEqual(result[4].text, expected_result[4].text)
        with self.assertRaises(IndexError):
            result[5]

    async def test_two_get_list_of_tag_by_string(self):
        """
        Test for function: app.repository.tags.get_list_of_tag_by_string()
        Checking whether an empty tag will be created and whitespace trimming
        """  
        test_string = "   , ok       , stop"
        expected_result = [
            Tag(text="ok"),
            Tag(text="stop")
        ]
        self.session.query().filter().first.return_value = None
        result = await get_list_of_tags_by_string(test_string, self.session)
        self.assertEqual(result[0].text, expected_result[0].text)
        self.assertEqual(result[1].text, expected_result[1].text)
        with self.assertRaises(IndexError):
            result[2]

    async def test_three_get_list_of_tag_by_string(self):
        """
        Test for function: app.repository.tags.get_list_of_tag_by_string()
        Test if input string empty
        """  
        test_string = ""
        self.session.query().filter().first.return_value = None
        result = await get_list_of_tags_by_string(test_string, self.session)
        self.assertEqual(result, [])

    async def test_get_tag_by_id_found(self):
        """
        Test for function: app.repository.tags.get_tag_by_id()
        Found return database model Tag
        """   
        expected_result = Tag(id=123, text="seccess test")
        self.session.query().filter().first.return_value = expected_result
        result = await get_tag_by_id(123, self.session)
        self.assertIsInstance(result, Tag)
        self.assertEqual(expected_result.id, result.id)
        self.assertEqual(expected_result.text, result.text)

    async def test_get_tag_by_id_not_found(self):
        """
        Test for function: app.repository.tags.get_tag_by_id()
        Not found return None
        """  
        self.session.query().filter().first.return_value = None
        result = await get_tag_by_id(123, self.session)
        self.assertIsNone(result)

    async def test_get_tags(self):
        expected_result = [
            Tag(id=1, text="new"),
            Tag(id=2, text="test"),
            Tag(id=3, text="tag"),
            Tag(id=4, text="help"),
            Tag(id=5, text="ok")
        ]
        self.session.query().offset().limit().all.return_value = expected_result
        result = await get_tags(self.session)
        self.assertEqual(expected_result, result)
        self.assertEqual(expected_result[0], result[0])
    
    async def test_get_test_by_text_found(self):
        """
        Test for function: app.repository.et_test_by_text()
        Found return database model Tag
        """  
        expected_result = Tag(id=1, text="expected_result")
        self.session.query().filter().first.return_value = expected_result
        result = await get_tag_by_text(expected_result.text, self.session)
        self.assertIsInstance(result, Tag)
        self.assertEqual(expected_result.text, result.text)

    async def test_get_test_by_text_not_found(self):
        """
        Test for function: app.repository.et_test_by_text()
        Not found return None
        """  
        expected_result = None
        self.session.query().filter().first.return_value = expected_result
        result = await get_tag_by_text("test string", self.session)
        self.assertIsNone(result)
    

if __name__ == "__main__":
    unittest.main()