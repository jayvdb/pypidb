import unittest

from pypidb._db import Database, reverse_mappings


class TestDB(unittest.TestCase):
    def test_basic(self):
        db = Database(store_fetch_list=True)
        url = db.find_project_scm_url("setuptools-scm")
        self.assertEqual(url, "https://github.com/pypa/setuptools_scm")


class TestData(unittest.TestCase):
    def test_reverse_mapping_urls(self):
        for key in reverse_mappings:
            self.assertEqual(key, key.lower())
