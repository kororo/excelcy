from excelcy import ExcelCy
from tests.test_base import BaseTestCase


class ExcelCyTestCase(BaseTestCase):
    def test_remote_execute(self):
        """ Test: Load and save training """

        self.assert_training(file_path='https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.xlsx')

    def test_execute(self):
        """ Test: Load and save training """

        self.assert_training(file_path=self.get_test_data_path('test_data_02.xlsx'))
        self.assert_training(file_path=self.get_test_data_path('test_data_03.xlsx'))

    def test_save(self):
        """ Test: save training """

        excelcy = ExcelCy.execute(file_path=self.get_test_data_path(fs_path='test_data_01.xlsx'))
        file_path = self.get_test_tmp_path(fs_path='test_data_01.xlsx')
        excelcy.save_storage(file_path=file_path)

        data = self.extract_storage(storage=excelcy.storage)
        excelcy.load(file_path=file_path)
        data2 = self.extract_storage(storage=excelcy.storage)

        assert data == data2

    def test_execute_phases(self):
        """ Test: executing phases """

        self.assert_training(file_path=self.get_test_data_path('test_data_04.xlsx'))
