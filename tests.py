# encoding:utf-8
# tests for lister; finding&removing of duplicates

# python3 -m unittest -v test_class_dictionary.py

<<<<<<< HEAD
print("*" * 75)

import unittest
# import shutil

import lister

SOURCE_FOLDER = '/Users/alexanderuperenko/Desktop/Python - my projects/duplifinder/test_folder'
DESTINATION = '/Users/alexanderuperenko/Desktop/Python - my projects/duplifinder/test_folder/destination'
=======
# DEVELOPMENT CURRENTLY FROZEN

print("*" * 75)

import unittest

import lister

SOURCE_FOLDER = '/Users/alexanderuperenko/Desktop/Python - my projects/duplifinder_test_folder'
DESTINATION = '/Users/alexanderuperenko/Desktop/Python - my projects/duplifinder_result'
>>>>>>> multiprocess

class MyTest(unittest.TestCase):

    def setUp(self):
        self.l = lister.Lister()
        self.l.get_folder_list(SOURCE_FOLDER)
<<<<<<< HEAD
=======
        self.l.print_folder_list()
>>>>>>> multiprocess
        self.l._create_hash_dictionary()
        self.l._find_duplicates()

    def test_move_duplicates(self):
        self.l._move_duplicates(DESTINATION)
<<<<<<< HEAD
        self.assertFalse(os.listdir(DESTINATION))
=======
        self.assertTrue(bool(os.listdir(DESTINATION)))
>>>>>>> multiprocess

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
