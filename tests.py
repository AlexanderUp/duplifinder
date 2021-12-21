# encoding:utf-8
# tests for Duplifinder, v.2.0

import unittest
from pathlib import Path

from dpf import Duplifinder
from config import TestConfig


class DuplifinderTest(unittest.TestCase):

    def setUp(self):
        self.path = Path(TestConfig.TEST_FOLDER).expanduser()
        self.path_to_be_excluded = None
        self.duplifinder = Duplifinder(self.path, self.path_to_be_excluded)
        self.duplifinder.extensions = dpf.MEDIA_EXTENSIONS

    def tearDown(self):
        pass

    @unittest.skip
    def test_create_db_backup(self):
        pass

    @unittest.skip
    def test_listing_functionality(self):
        self.duplifinder.update_db()
        self.print_duplicates_list()


if __name__ == '__main__':
    unittest.main()
