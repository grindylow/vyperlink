from element import *
import unittest

class BasicTests(unittest.TestCase):

    def test_basic_elements(self):
        self.assertEqual(1,2)

    def test_another_test(self):
        self.assertEqual(2,2)

if __name__ == "__main__":
    pass
    #unittest.main()


    
