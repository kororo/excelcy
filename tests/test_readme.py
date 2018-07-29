from excelcy import ExcelCy, cli
from excelcy.storage import Config
from tests.test_base import BaseTestCase


class ReadmeTestCase(BaseTestCase):
    def test_readme_01(self):
        """ Test: code snippet found in README.rst """

        self.assert_training(file_path=self.get_test_data_path('test_data_01.xlsx'))

    def test_readme_02(self):
        """ Test: code snippet found in README.rst """

        excelcy = ExcelCy.execute(file_path=self.get_test_data_path(fs_path='test_data_01.xlsx'))
        doc = excelcy.nlp('Google rebrands its business apps')
        assert doc.ents[0].label_ == 'ORG'

    def test_readme_03(self):
        """ Test: code snippet found in README.rst """

        excelcy = ExcelCy()
        excelcy.storage.base_path = self.test_data_path
        excelcy.storage.config = Config(nlp_base='en_core_web_sm', train_iteration=2, train_drop=0.2)
        excelcy.storage.source.add(kind='text', value='Robertus Johansyah is the maintainer ExcelCy')
        excelcy.storage.source.add(kind='textract', value='source/source_01.txt')
        excelcy.storage.prepare.add(kind='phrase', value='Uber', entity='ORG')
        excelcy.storage.prepare.add(kind='phrase', value='Robertus Johansyah', entity='PERSON')
        excelcy.discover()
        excelcy.prepare()
        excelcy.train()
        assert excelcy.nlp('Uber blew through $1 million a week').ents[0].label_ == 'ORG'
        assert excelcy.nlp('Robertus Johansyah is maintainer ExcelCy').ents[0].label_ == 'PERSON'

    def test_readme_04(self):
        """ Test: code snippet found in README.rst """

        # load first and confirm Himalayas is PRODUCT
        excelcy = ExcelCy.execute(file_path=self.get_test_data_path(fs_path='test_data_05.xlsx'))
        gold = excelcy.storage.train.items.get('1').items.get('1.1')
        assert gold.subtext == 'Himalayas' and gold.entity == 'PRODUCT'

        # retrain and set the entity of Himalaya to PLACE
        excelcy = ExcelCy.execute(file_path=self.get_test_data_path(fs_path='test_data_05a.xlsx'))
        gold = excelcy.storage.train.items.get('1').items.get('1.1')
        assert gold.subtext == 'Himalayas' and gold.entity == 'FAC'

    def test_readme_05(self):
        """ Test: code snippet found in README.rst """

        cli.main(['', 'execute', self.get_test_data_path('test_data_01.xlsx')])
