from excelcy import ExcelCy
from excelcy.storage import Config
from tests.test_base import BaseTestCase


class TestExcelCy(BaseTestCase):
    def test_execute(self):
        """ Test: Load and save training """

        self.assert_training(file_path=self.get_test_data_path('test_data_02.xlsx'))

    def test_remote_execute(self):
        """ Test: Load and save training """

        self.assert_training(file_path='https://github.com/kororo/excelcy/raw/master/tests/data/test_data_03.xlsx')
