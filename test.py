import os
from manipulate_stop_area import read_json, fetchnameandid,findurl, findname, transform_in_csv
import unittest
import requests
import json


class TestJsonInPath(unittest.TestCase):
    def test_check_file_exist(self):
        directory_path = './stop_areas.json' # somepath
        self.assertTrue(os.path.exists(directory_path))

    def test_find_id_and_name(self):
        self.assertTrue(fetchnameandid())

    def findlinks(self):
        self.assertTrue(findurl())

    def test_find_name(self):
        self.assertTrue(findname())
    
    def test_transform_in_csv(self):
        directory_path = './data.csv'
        self.assertTrue(os.path.exists(directory_path))

if __name__ == '__main__':
    unittest.main()

    
