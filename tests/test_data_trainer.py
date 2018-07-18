from excelcy import ExcelCy
from tests.test_base import BaseTestCase


class TestDataTrainer(BaseTestCase):
    def test_train(self):
        # test: train with single row
        # Annotate Uber manually to ORG
        test_path = self.get_test_data_path('test_data_01.xlsx')
        excelcy = ExcelCy()
        excelcy.train(data_path=test_path, options={'clean': True})

    def test_train_matcher_nlp(self):
        # test: train with pipe matcher
        # Annotate Uber with nlp pattern phrase matcher
        test_path = self.get_test_data_path('test_data_02.xlsx')
        tests = {'1': {('$1 million', 'MONEY'), ('a week', 'DATE')}}
        self.assert_ents(data_path=test_path, options={'clean': True}, tests=tests)

    def test_train_matcher_regex(self):
        # test: train with pipe matcher
        # Annotate aweek with regex pattern matcher
        test_path = self.get_test_data_path('test_data_03.xlsx')
        tests = {'1': {('Uber', 'ORG')}}
        self.assert_ents(data_path=test_path, options={'clean': True}, tests=tests)

    def test_train_smash(self):
        # disabled for now, 2880 sentences test takes 1286 seconds
        pass

        # test: train with 2880 sentences
        # test_path = self.get_test_data_path('test_data_05.xlsx')
        # self.assert_ents(data_path=test_path, options={'clean': True})
