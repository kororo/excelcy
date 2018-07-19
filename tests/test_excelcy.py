import pytest
from excelcy import ExcelCy, DataTrainer, errors
from tests.test_base import BaseTestCase


class TestExcelCy(BaseTestCase):
    def test_clean(self):
        # test: test the clean process
        test_path = self.get_test_data_path('test_data_01.xlsx')
        excelcy = ExcelCy()
        excelcy.train(data_path=test_path, options={'clean': True})
        excelcy.train(data_path=test_path, options={'clean': True})

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

        # re-create the data
        data_path = self.get_test_dir_path('test_data_01.xlsx')
        data_trainer.data_save(data_path)

        # reload it again
        data_trainer2 = DataTrainer(data_path=data_path)

        # and compare them, it should be exact the same
        assert data_trainer.data_train == data_trainer2.data_train
        assert data_trainer.data_config == data_trainer2.data_config

    def test_readme(self):
        import os
        import spacy
        import tempfile
        from excelcy import ExcelCy

        # create nlp data model based on "en_core_web_sm" and save it to "test_data_01"
        base = 'en_core_web_sm'
        nlp = spacy.load(base)

        # save and reload to verify

        # create dir nlp
        tmp_path = os.environ.get('EXCELCY_TEMP_PATH', tempfile.gettempdir())
        name = os.path.join(tmp_path, 'nlp/test_data_01')
        os.makedirs(name, exist_ok=True)
        # save it
        nlp.to_disk(name)
        nlp = spacy.load(name)

        # test the NER
        text = 'Uber blew through $1 million a week'
        doc = nlp(text)
        ents = set([(ent.text, ent.label_) for ent in doc.ents])

        # this shows current model in test_data_01, has no "Uber" identified as ORG
        assert ents == {('$1 million', 'MONEY')}

        # lets train
        excelcy = ExcelCy()
        # copy excel from https://github.com/kororo/excelcy/tree/master/excelcy/tests/data/test_data_01.xlsx
        # ensure name is "nlp/test_data_01" inside config sheet.
        # ensure directory data model "nlp/test_data_01" is created and exist.
        test_path = self.get_test_data_path('test_data_01.xlsx')
        excelcy.train(data_path=test_path)

        # reload the data model
        nlp = spacy.load(name)

        # test the NER
        doc = nlp(text)
        ents = set([(ent.text, ent.label_) for ent in doc.ents])

        # this shows current model in test_data_01, has "Uber" identified as ORG
        assert ents == {('Uber', 'ORG'), ('$1 million', 'MONEY')}

    def test_readme_simple(self):
        from excelcy import ExcelCy

        test_path = self.get_test_data_path('test_data_28.xlsx')
        excelcy = ExcelCy()
        excelcy.train(data_path=test_path)

    def test_init_errors(self):
        with pytest.raises(ValueError) as excinfo:
            test_path = self.get_test_data_path('test_data_28.xlsx')
            data_trainer = DataTrainer(data_path=test_path)
            data_trainer.reset()
            data_trainer.train()
        assert str(excinfo.value) == errors.Errors.E001
