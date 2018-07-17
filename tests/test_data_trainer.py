from excelcy.excelcy import DataTrainer
from tests.test_base import TestBase


class TestDataTrainer(TestBase):
    def test_train(self):
        test_path = self.get_test_data_path('data1.xlsx')
        training = DataTrainer(data_path=test_path)
        training.train()
