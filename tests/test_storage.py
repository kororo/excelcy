from excelcy import utils
from excelcy.storage import Storage
from tests.test_base import BaseTestCase


class TestExcelCy(BaseTestCase):
    def test_create_storage(self):
        storage = Storage()
        storage.source.add(kind='text', value='Uber blew through $1 million a week. Android Pay expands to Canada.')
        storage.source.add(kind='textract', value='source/test.txt')
        storage.prepare.add(kind='phrase', value='google', entity='PRODUCT')
        storage.prepare.add(kind='regex', value='Uber?', entity='ORG')
        storage.prepare.add(kind='index', value='$1 million', entity='TIME')
        train = storage.train.add(text='Uber blew through $1 million a week.')
        train.add(subtext='Uber', span=(0, 4), entity='ORG')
        train.add(subtext='$1 million', span=(18, 28), entity='MONEY')
        train = storage.train.add(text='Android Pay expands to Canada.')
        train.add(subtext='Android Pay', span=(0, 11), entity='PRODUCT')
        # print(json.dumps(storage.items(), indent=2))
        # utils.yaml_save(storage.items(), 'test.yml')
