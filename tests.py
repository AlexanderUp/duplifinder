# encoding:utf-8
# tests for lister; finding&removing of duplicates

# python3 -m unittest -v test_class_dictionary.py

# DEVELOPMENT CURRENTLY FROZEN

print("*" * 75)

import unittest

import lister

SOURCE_FOLDER = '/Users/alexanderuperenko/Desktop/Python - my projects/duplifinder_test_folder'
DESTINATION = '/Users/alexanderuperenko/Desktop/Python - my projects/duplifinder_result'

class MyTest(unittest.TestCase):

    def setUp(self):
        self.l = lister.Lister()
        self.l.get_folder_list(SOURCE_FOLDER)
        self.l.print_folder_list()
        self.l._create_hash_dictionary()
        self.l._find_duplicates()

    def tearDown(self):
        pass

    def test_move_duplicates(self):
        self.l._move_duplicates(DESTINATION)
        self.assertFalse(os.listdir(DESTINATION))
        self.assertTrue(bool(os.listdir(DESTINATION)))


if __name__ == '__main__':
    unittest.main()
