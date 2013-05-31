#!/usr/bin/python
from element import *
from pymongo import MongoClient
import unittest

class BasicTests(unittest.TestCase):

    def setUp(self):
        self.client = MongoClient('localhost',27017)
        self.db = self.client.UnitTestingDB
        self.coll = self.db.elements

    def test_create_basic_elements(self):
        a = TextElement()
        a.save(self.coll)
        b = TextElement()
        b.save(self.coll)

    def test_create_and_retrieve_elements(self):
        a = TextElement(v_id="TEXT.73",v_content="Whirl whirl whirl.\nHurl.")
        a.save(self.coll)
        print a

        b = Element.retrieveFromDB(self.coll,"TEXT.73")
        print b

    def test_another_test(self):
        self.assertEqual(2,2)

if __name__ == "__main__":
    unittest.main()


    
