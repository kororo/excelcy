from excelcy import ExcelCy
from excelcy.pipe import MatcherPipe
from excelcy.storage import Config
from tests.test_base import BaseTestCase


class PipeTestCase(BaseTestCase):
    def test_matcher(self):
        """ Test: Matcher """

        excelcy = ExcelCy()
        excelcy.storage.config = Config(nlp_base='en_core_web_sm', train_iteration=2, train_drop=0.2)
        nlp = excelcy.create_nlp()
        patterns = [
            {'kind': 'phrase', 'value': 'thisisrandom', 'entity': 'PRODUCT'},
            {'kind': 'regex', 'value': 'thatis(.+)', 'entity': 'PRODUCT'}
        ]
        nlp.add_pipe(MatcherPipe(nlp=nlp, patterns=patterns))  # type: MatcherPipe
        doc = nlp('thisisrandom thatisrandom')
        assert doc.ents[0].label_ == 'PRODUCT' and doc.ents[1].label_ == 'PRODUCT'

    def test_execute(self):
        """ Test: Load and save training """

        self.assert_training(file_path=self.get_test_data_path('test_data_02.xlsx'))
        self.assert_training(file_path=self.get_test_data_path('test_data_03.xlsx'))

    def test_save(self):
        """ Test: save training """

        excelcy = ExcelCy.execute(file_path=self.get_test_data_path(fs_path='test_data_01.xlsx'))
        file_path = self.get_test_tmp_path(fs_path='test_data_01.xlsx')
        excelcy.save_storage(file_path=file_path)
        excelcy.load(file_path=file_path)
