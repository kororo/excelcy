from excelcy import ExcelCy
from excelcy.storage import Config

# test_string = 'Android Pay expands to Canada'
# excelcy = ExcelCy()
# excelcy.storage.config = Config(nlp_base='en_core_web_sm', train_iteration=50, train_drop=0.2)
# doc = excelcy.nlp(test_string)
# # showing no ORG
# print([(ent.label_, ent.text) for ent in doc.ents])
# excelcy.storage.source.add(kind='text', value=test_string)
# excelcy.discover()
# excelcy.storage.prepare.add(kind='phrase', value='Android Pay', entity='PRODUCT')
# excelcy.prepare()
# excelcy.train()
# doc = excelcy.nlp(test_string)
# print([(ent.label_, ent.text) for ent in doc.ents])



# FAILED tests/test_excelcy.py::ExcelCyTestCase::test_execute - AssertionError: assert ('$1', 'MONEY') in {('$1 million', 'MONEY'), ('Uber', 'ORG')}
# FAILED tests/test_pipe.py::PipeTestCase::test_execute - AssertionError: assert ('$1', 'MONEY') in {('$1 million', 'MONEY'), ('Uber', 'ORG')}
# FAILED tests/test_readme.py::ReadmeTestCase::test_readme_04 - AssertionError: assert ('China' == 'Himalayas'



excelcy = ExcelCy()
doc = excelcy.nlp('Android Pay expands to Canada')
print([(ent.label_, ent.text) for ent in doc.ents])
excelcy = ExcelCy.execute(file_path='tests/data/test_data_03.xlsx')
doc = excelcy.nlp('Android Pay expands to Canada')
print([(ent.label_, ent.text) for ent in doc.ents])

