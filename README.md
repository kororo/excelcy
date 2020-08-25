ExcelCy
=======

[![Build Status](https://travis-ci.com/kororo/excelcy.svg?branch=master)](https://travis-ci.com/kororo/excelcy)
[![Coverage Status](https://coveralls.io/repos/github/kororo/excelcy/badge.svg)](https://coveralls.io/github/kororo/excelcy)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/excelcy.svg)](https://pypi.python.org/project/excelcy/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/excelcy)](https://pypi.python.org/project/excelcy/)

* * * * *

ExcelCy is a NER trainer from XLSX, PDF, DOCX, PPT, PNG or JPG. ExcelCy uses spaCy framework to match Entity with PhraseMatcher or Matcher in regular expression.

ExcelCy is convenience
----------------------

This is example taken from spaCy documentation, [Simple Style Training](https://spacy.io/usage/training#training-simple-style). It demonstrates how to train NER using spaCy:

```python
import spacy
import random

TRAIN_DATA = [
     ("Uber blew through $1 million a week", {'entities': [(0, 4, 'ORG')]}), # note: it is required to supply the character position
     ("Google rebrands its business apps", {'entities': [(0, 6, "ORG")]})] # note: it is required to supply the character position

nlp = spacy.blank('en')
optimizer = nlp.begin_training()
for i in range(20):
    random.shuffle(TRAIN_DATA)
    for text, annotations in TRAIN_DATA:
        nlp.update([text], [annotations], sgd=optimizer)

nlp.to_disk('test_model')
```

The **TRAIN\_DATA**, describes sentences and annotated entities to be trained. It is cumbersome to always count the characters. With ExcelCy, (start,end) characters can be omitted.

```python
# install excelcy
# pip install excelcy

# download the en model from spacy
# python -m spacy download en"

# run this inside python or file
from excelcy import ExcelCy

# Test: John is the CEO of this_is_a_unique_company_name
excelcy = ExcelCy()
# by default it is assume the nlp_base using model en_core_web_sm
# excelcy.storage.config = Config(nlp_base='en_core_web_sm')
# if you have existing model, use this
# excelcy.storage.config = Config(nlp_path='/path/model')
doc = excelcy.nlp('John is the CEO of this_is_a_unique_company_name')
# it will show no company entities
print([(ent.label_, ent.text) for ent in doc.ents])
# run this in root of repo or https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.xlsx
excelcy = ExcelCy.execute(file_path='tests/data/test_data_01.xlsx')
# use the nlp object as per spaCy API
doc = excelcy.nlp('John is the CEO of this_is_a_unique_company_name')
# now it recognise the company name
print([(ent.label_, ent.text) for ent in doc.ents])
# NOTE: if not showing, remember, it may be required to increase the "train_iteration" or lower the "train_drop", the "config" sheet in Excel
```

ExcelCy is friendly
-------------------

By default, ExcelCy training is divided into phases, the example Excel file can be found in [tests/data/test\_data\_01.xlsx](https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.xlsx):

### 1. Discovery

The first phase is to collect sentences from data source in sheet "source". The data source can be either:

-   Text: Direct sentence values.
-   Files: PDF, DOCX, PPT, PNG or JPG will be parsed using
    [textract](https://github.com/deanmalmgren/textract).

Note: See textract source examples in [tests/data/test\_data\_03.xlsx](https://github.com/kororo/excelcy/raw/master/tests/data/test_data_03.xlsx)
Note: Dependencies "textract" is not included in the ExcelCy, it is required to add manually

### 2. Preparation

Next phase, the Gold annotation needs to be defined in sheet "prepare", based on:

-   Current Data Model: Using spaCy API of **nlp(sentence).ents**
-   Phrase pattern: Robbie, Uber, Google, Amazon
-   Regex pattern: \^([0-1]?[0-9]|2[0-3]):[0-5][0-9]\$

All annotations in here are considered as Gold annotations, which described in [here](https://spacy.io/usage/training#example-new-entity-type).

### 3. Training

Main phase of NER training, which described in [Simple Style Training](https://spacy.io/usage/training#training-simple-style).
The data is iterated from sheet "train", check sheet "config" to control the parameters.

### 4. Consolidation

The last phase, is to test/save the results and repeat the phases if required.

ExcelCy is flexible
-------------------

Need more specific export and phases? It is possible to control it using phase API.
This is the illustration of the real-world scenario:

1.  Train from
    [tests/data/test\_data\_05.xlsx](https://github.com/kororo/excelcy/raw/master/tests/data/test_data_05.xlsx)

    ```shell script
    # download the dataset
    $ wget https://github.com/kororo/excelcy/raw/master/tests/data/test_data_05.xlsx
    # this will create a directory and file "export/train_05.xlsx"
    $ excelcy execute test_data_05.xlsx
    ```

2.  Open the result in "export/train\_05.xlsx", it shows all identified sentences from source given. However, there is error in the "Himalayas" as identified as "PRODUCT".
    
3.  To fix this, add phrase matcher for "Himalayas = FAC". It is illustrated in
    [tests/data/test\_data\_05a.xlsx](https://github.com/kororo/excelcy/raw/master/tests/data/test_data_05a.xlsx)
    
4.  Train again and check the result in "export/train\_05a.xlsx"

    ```shell script
    # download the dataset
    $ wget https://github.com/kororo/excelcy/raw/master/tests/data/test_data_05a.xlsx
    # this will create a directory "nlp/data" and file "export/train_05a.xlsx"
    $ excelcy execute test_data_05a.xlsx
    ```

5.  Check the result that there is backed up nlp data model in "nlp" and the result is corrected in "export/train\_05a.xlsx"

6.  Keep training the data model, if there is unexpected behaviour, there is backup data model in case needed.

ExcelCy is comprehensive
------------------------

Under the hood, ExcelCy has strong and well-defined data storage. At any given phase above, the data can be inspected.

```python
from excelcy import ExcelCy
from excelcy.storage import Config

# Test: John is the CEO of this_is_a_unique_company_name
excelcy = ExcelCy()
excelcy.storage.config = Config(nlp_base='en_core_web_sm', train_iteration=10, train_drop=0.2)
doc = excelcy.nlp('John is the CEO of this_is_a_unique_company_name')
# showing no ORG
print([(ent.label_, ent.text) for ent in doc.ents])
excelcy.storage.source.add(kind='text', value='John is the CEO of this_is_a_unique_company_name')
excelcy.discover()
excelcy.storage.prepare.add(kind='phrase', value='this_is_a_unique_company_name', entity='ORG')
excelcy.prepare()
excelcy.train()
doc = excelcy.nlp('John is the CEO of this_is_a_unique_company_name')
# ORG now is recognised
print([(ent.label_, ent.text) for ent in doc.ents])
# NOTE: if not showing, remember, it may be required to increase the "train_iteration" or lower the "train_drop", the "config" sheet in Excel
```

Features
--------

-   Load multiple data sources such as Word documents, PowerPoint presentations, PDF or images.
-   Import/Export configuration with JSON, YML or Excel.
-   Add custom Entity labels.
-   Rule based phrase matching using [PhraseMatcher](https://spacy.io/usage/linguistic-features#adding-phrase-patterns)
-   Rule based matching using [regex + Matcher](https://spacy.io/usage/linguistic-features#regex)
-   Train Named Entity Recogniser with ease

Install
-------

Either use the famous pip or clone this repository and execute the
setup.py file.

```shell script
$ pip install excelcy
# ensure you have the language model installed before
$ spacy download en
```

Train
-----

To train the spaCy model:

```python
from excelcy import ExcelCy
excelcy = ExcelCy.execute(file_path='test_data_01.xlsx')
```

Note: [tests/data/test\_data\_01.xlsx](https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.xlsx)

CLI
---

ExelCy has basic CLI command for execute:

```shell script
$ excelcy execute https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.xlsx
```

Test
----

Run test by installing packages and run tox

```shell script
$ pip install poetry tox
$ tox
$ tox -e py36 -- tests/test_readme.py
```

For hot-reload development coding
```shell script
$ npm i -g nodemon
$ nodemon
```

Data Definition
---------------

ExcelCy has data definition which expressed in [api.yml](https://github.com/kororo/excelcy/raw/master/data/api.yml).
As long as, data given in this specific format and structure, ExcelCy will able to support any type of data format.
Check out, the Excel file format in [api.xlsx](https://github.com/kororo/excelcy/raw/master/data/api.xlsx).
Data classes are defined with [attrs](https://github.com/python-attrs/attrs),
check in [storage.py](https://github.com/kororo/excelcy/raw/master/excelcy/storage.py) for more detail.

Publishing
----------
```shell script
# this is note for contributors
# ensure locally tests all running
npm run test

# prepare for new version
poetry version 0.4.1
npm run export

# make changes in the git, especially release branch and check in the travis
# https://travis-ci.com/github/kororo/excelcy

# if all goes well, push to master

```
FAQ
---

**What is that idx columns in the Excel sheet?**

The idea is to give reference between two things. Imagine in sheet "train", like to know where the sentence generated
from in sheet "source". And also, the nature of Excel, you can sort things, this is the safe guard to keep things in
the correct order.

**Can ExcelCy import/export to X, Y, Z data format?**

ExcelCy has strong and well-defined data storage, thanks to [attrs](https://github.com/python-attrs/attrs).
It is possible to import/export data in any format.

**Error: ModuleNotFoundError: No module named 'pip'**

There are lots of possibility on this. Try to lower pip version (it was buggy for version 19.0.3).

**ExcelCy accepts suggestions/ideas?**

Yes! Please submit them into new issue with label "enhancement".

Acknowledgement
---------------

This project uses other awesome projects:

-   [attrs](https://github.com/python-attrs/attrs): Python Classes Without Boilerplate.
-   [pyexcel](https://github.com/pyexcel/pyexcel): Single API for reading, manipulating and writing data in csv, ods, xls, xlsx and xlsm files.
-   [pyyaml](https://github.com/yaml/pyyaml): The next generation YAML parser and emitter for Python.
-   [spacy](https://github.com/explosion/spaCy): Industrial-strength Natural Language Processing (NLP) with Python and Cython.
-   [textract](https://github.com/deanmalmgren/textract): extract text from any document. no muss. no fuss.

