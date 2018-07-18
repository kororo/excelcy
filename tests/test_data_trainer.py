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
        tests = {'1': {('Uber', 'ORG')}}
        self.assert_ents(data_path=test_path, options={'clean': True}, tests=tests)

        # self.assert_ents(data_path=test_path)
        # test: train based on data in https://spacy.io/usage/training#training-data

    def test_train_matcher_regex(self):
        # test: train with pipe matcher
        # Annotate aweek with regex pattern matcher
        test_path = self.get_test_data_path('test_data_03.xlsx')
        tests = {'1': {('a week', 'DATE')}}
        self.assert_ents(data_path=test_path, options={'clean': True}, tests=tests)
