# encoding:utf-8
# tests for lister; finding&removing of duplicates

# python3 -m unittest -v test_class_dictionary.py

print("*" * 75)

import unittest
# import shutil

import lister

SOURCE_FOLDER = '/Users/alexanderuperenko/Desktop/Python - my projects/duplifinder/test_folder'
DESTINATION = '/Users/alexanderuperenko/Desktop/Python - my projects/duplifinder/test_folder/destination'

class MyTest(unittest.TestCase):

    def setUp(self):
        self.l = lister.Lister()
        self.l.get_folder_list(SOURCE_FOLDER)
        self.l._create_hash_dictionary()
        self.l._find_duplicates()

    def test_move_duplicates(self):
        self.l._move_duplicates(DESTINATION)
        self.assertFalse(os.listdir(DESTINATION))

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
