from excelcy.storage import Storage
from tests.test_base import BaseTestCase


class StorageTestCase(BaseTestCase):
    def test_load_save_excel(self):
        storage = Storage()
        storage.load(file_path=self.get_test_data_path(fs_path='test_data_03.xlsx'))
        data1 = storage.items()
        tmp_path = self.get_test_tmp_path(fs_path='test_data_03.xlsx')
        storage.save(file_path=tmp_path)
        storage.load(file_path=tmp_path)
        data2 = storage.items()
        assert data1 == data2

    def test_load_save_yml(self):
        storage = Storage()
        storage.load(file_path=self.get_test_data_path(fs_path='test_data_03.xlsx'))
        data1 = storage.items()
        tmp_path = self.get_test_tmp_path(fs_path='test_data_03.yml')
        storage.save(file_path=tmp_path)
        storage.load(file_path=tmp_path)
        data2 = storage.items()
        assert data1 == data2
