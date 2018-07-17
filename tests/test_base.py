import json
import os


class TestBase(object):
    def setup_class(self):
        # set path
        current_path = os.path.dirname(os.path.abspath(__file__))
        self.test_data_path = os.path.join(current_path, 'data')

    def teardown_class(self):
        pass

    def get_test_data_path(self, fs_path: str):
        return os.path.join(self.test_data_path, fs_path)

    def get_test_data_file(self, fs_path: str):
        return open(self.get_test_data_path(fs_path=fs_path)).read()

    def get_test_data_json(self, fs_path: str):
        return json.loads(self.get_test_data_file(fs_path=fs_path))
