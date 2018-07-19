import os

import spacy
from excelcy import ExcelCy, DataTrainer
from tests.test_base import BaseTestCase


class TestDataTrainer(BaseTestCase):
    def test_clean(self):
        # test: test the clean process
        test_path = self.get_test_data_path('test_data_01.xlsx')
        excelcy = ExcelCy()
        excelcy.train(data_path=test_path, options={'clean': True})
        excelcy.train(data_path=test_path, options={'clean': True})

    def test_missing_ner_pipe(self):
        base = 'en_core_web_sm'
        nlp = spacy.load(base)
        # lets remove ner to simulate
        nlp.remove_pipe('ner')

        # save and reload to verify
        name = 'nlp/test_data_01'
        # create dir nlp
        os.makedirs(name, exist_ok=True)
        # save it
        nlp.to_disk(name)

        # lets try it
        test_path = self.get_test_data_path('test_data_01.xlsx')
        self.assert_ents(data_path=test_path)

    def test_train_basic(self):
        # test: train with single row
        # Annotate Uber manually to ORG
        test_path = self.get_test_data_path('test_data_01.xlsx')
        self.assert_ents(data_path=test_path)

    def test_train_matcher_nlp(self):
        # test: train with pipe matcher
        # Annotate Uber with nlp pattern phrase matcher
        test_path = self.get_test_data_path('test_data_02.xlsx')
        tests = {'1': {('$1 million', 'MONEY'), ('a week', 'DATE')}}
        self.assert_ents(data_path=test_path, tests=tests)

    def test_train_matcher_regex(self):
        # test: train with pipe matcher
        # Annotate aweek with regex pattern matcher
        test_path = self.get_test_data_path('test_data_03.xlsx')
        tests = {'1': {('Uber', 'ORG')}}
        self.assert_ents(data_path=test_path, tests=tests)

    def test_train_complex(self):
        # test: train with more complex data including given span
        test_path = self.get_test_data_path('test_data_04.xlsx')
        self.assert_ents(data_path=test_path)

    def test_train_smash(self):
        # disabled for now, 2880 sentences test takes 1286 seconds
        pass

        # test: train with 2880 sentences
        # test_path = self.get_test_data_path('test_data_05.xlsx')
        # self.assert_ents(data_path=test_path, options={'clean': True})

    def test_read_write(self):
        # read the data first
        test_path = self.get_test_data_path('test_data_01.xlsx')
        data_trainer = DataTrainer(data_path=test_path)

        # prepare the dir
        nlp_path = self.get_test_data_path('nlp/nlp')
        os.makedirs(nlp_path, exist_ok=True)
        # re-create the data
        test_path2 = self.get_test_data_path('nlp/test_data_01.xlsx')
        data_trainer.data_save(test_path2)

        # reload it again
        data_trainer2 = DataTrainer(data_path=test_path2)

        # and compare them, it should be exact the same
        assert data_trainer.data_train == data_trainer2.data_train
        assert data_trainer.data_config == data_trainer2.data_config
