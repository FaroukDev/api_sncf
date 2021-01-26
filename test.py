import os
from manipulate_stop_area import read_json
import unittest

class TestJsonInPath(unittest.TestCase):
    def test_check_file_exist(self):
        directory_path = './stop_areas.json' # somepath
        self.assertTrue(os.path.exists(directory_path))
        
if __name__ == '__main__':
    unittest.main()