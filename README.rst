ExcelCy
=======

.. image:: https://badge.fury.io/py/excelcy.svg
    :target: https://badge.fury.io/py/excelcy

.. image:: https://travis-ci.com/kororo/excelcy.svg?branch=master
    :target: https://travis-ci.com/kororo/excelcy

.. image:: https://coveralls.io/repos/github/kororo/excelcy/badge.svg?branch=master
    :target: https://coveralls.io/github/kororo/excelcy?branch=master

.. image:: https://badges.gitter.im/excelcy.png
    :target: https://gitter.im/excelcy
    :alt: Gitter

------

ExcelCy is a toolkit to integrate Excel to spaCy NLP training experiences. Training NER using XLSX from PDF, DOCX, PPT, PNG or JPG. ExcelCy has pipeline to match Entity with PhraseMatcher or Matcher in regular expression.

ExcelCy is Powerful
-------------------

`Simple Style Training <https://spacy.io/usage/training#training-simple-style>`__, from spaCy documentation, demonstrates how to train NER using spaCy:

.. code-block:: python

    TRAIN_DATA = [
         ("Uber blew through $1 million a week", {'entities': [(0, 4, 'ORG')]}),
         ("Google rebrands its business apps", {'entities': [(0, 6, "ORG")]})]

    nlp = spacy.blank('en')
    optimizer = nlp.begin_training()
    for i in range(20):
        random.shuffle(TRAIN_DATA)
        for text, annotations in TRAIN_DATA:
            nlp.update([text], [annotations], sgd=optimizer)
    nlp.to_disk('/model')

The **TRAIN_DATA**, describes sentences and annotated entities to be trained. It is cumbersome to always count the characters. With ExcelCy, (start,end) characters can be omitted.

.. code-block:: python

    # download the en model from spacy
    # python -m spacy download en"
    from excelcy import ExcelCy
    # collect sentences, annotate Entities and train NER using spaCy
    excelcy = ExcelCy.execute(file_path='https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.xlsx')
    # use the nlp object as per spaCy API
    doc = excelcy.nlp('Google rebrands its business apps')
    # or save_storage it for faster bootstrap for application
    excelcy.nlp.to_disk('/model')


ExcelCy is Friendly
-------------------

By default, ExcelCy training is divided into phases, the example Excel file can be found in `tests/data/test_data_01.xlsx <https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.xlsx>`__:

1. Discovery
^^^^^^^^^^^^

The first phase is to collect sentences from data source in sheet "source". The data source can be either:

- Text: Direct sentence values.
- Files: PDF, DOCX, PPT, PNG or JPG will be parsed using `textract <https://github.com/deanmalmgren/textract>`__.

2. Preparation
^^^^^^^^^^^^^^

Next phase, the Gold annotation needs to be defined in sheet "prepare", based on:

- Current Data Model: Using spaCy API of **nlp(sentence).ents**
- Phrase pattern: Robertus Johansyah, Uber, Google, Amazon
- Regex pattern: ^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$

All annotations in here are considered as Gold annotations, which described in `here <https://spacy.io/usage/training#example-new-entity-type>`__.

3. Training
^^^^^^^^^^^

Main phase of NER training, which described in `Simple Style Training <https://spacy.io/usage/training#training-simple-style>`__. The data is iterated from sheet "train", check sheet "config" to control the parameters.

4. Consolidation
^^^^^^^^^^^^^^^^

The last phase, is to test/save the results and repeat the phases if required.

ExcelCy is Flexible
-------------------

Need more specific export and phases? It is possible to control it using phase API. This is the illustration of the real-world scenario:

1. Train from `tests/data/test_data_05.xlsx <https://github.com/kororo/excelcy/raw/master/tests/data/test_data_05.xlsx>`__

    .. code-block:: bash

        # download the dataset
        $ wget https://github.com/kororo/excelcy/raw/master/tests/data/test_data_05.xlsx
        # this will create a directory and file "export/train_05.xlsx"
        $ excelcy execute test_data_05.xlsx

2. Open the result in "export/train_05.xlsx", it shows all identified sentences from source given. However, there is error in the "Himalayas" as identified as "PRODUCT".
3. To fix this, add phrase matcher for "Himalayas = FAC". It is illustrated in `tests/data/test_data_05a.xlsx <https://github.com/kororo/excelcy/raw/master/tests/data/test_data_05a.xlsx>`__
4. Train again and check the result in "export/train_05a.xlsx"

    .. code-block:: bash

        # download the dataset
        $ wget https://github.com/kororo/excelcy/raw/master/tests/data/test_data_05a.xlsx
        # this will create a directory "nlp/data" and file "export/train_05a.xlsx"
        $ excelcy execute test_data_05a.xlsx

5. Check the result that there is backed up nlp data model in "nlp" and the result is corrected in "export/train_05a.xlsx"
6. Keep training the data model, if there is unexpected behaviour, there is backup data model in case needed.

ExcelCy is Comprehensive
------------------------

Under the hood, ExcelCy has strong and well-defined data storage. At any given phase above, the data can be inspected.

.. code-block:: python

    from excelcy import ExcelCy

    excelcy = ExcelCy()
    # load configuration from XLSX or YML or JSON
    # excelcy.load(file_path='test_data_01.xlsx')
    # or define manually
    excelcy.storage.config = Config(nlp_base='en_core_web_sm', train_iteration=2, train_drop=0.2)
    print(json.dumps(excelcy.storage.as_dict(), indent=2))

    # add sources
    excelcy.storage.source.add(kind='text', value='Robertus Johansyah is the maintainer ExcelCy')
    excelcy.storage.source.add(kind='textract', value='tests/data/source/test_source_01.txt')
    excelcy.discover()
    print(json.dumps(excelcy.storage.as_dict(), indent=2))

    # add phrase matcher Robertus Johansyah -> PERSON
    excelcy.storage.prepare.add(kind='phrase', value='Robertus Johansyah', entity='PERSON')
    excelcy.prepare()
    print(json.dumps(excelcy.storage.as_dict(), indent=2))

    # train it
    excelcy.train()
    print(json.dumps(excelcy.storage.as_dict(), indent=2))

    # test it
    doc = excelcy.nlp('Robertus Johansyah is maintainer ExcelCy')
    print(json.dumps(excelcy.storage.as_dict(), indent=2))


Features
--------

- Load multiple data sources such as Word documents, PowerPoint presentations, PDF or images.
- Import/Export configuration with JSON, YML or Excel.
- Add custom Entity labels.
- Rule based phrase matching using `PhraseMatcher <https://spacy.io/usage/linguistic-features#adding-phrase-patterns>`__
- Rule based matching using `regex + Matcher <https://spacy.io/usage/linguistic-features#regex>`__
- Train Named Entity Recogniser with ease

Install
-------

Either use the famous pip or clone this repository and execute the setup.py file.

.. code-block:: bash

    $ pip install excelcy
    # ensure you have the language model installed before
    $ spacy download en

Train
-----

To train the spaCy model:

.. code-block:: python

    from excelcy import ExcelCy
    excelcy = ExcelCy.execute(file_path='test_data_01.xlsx')

Note: `tests/data/test_data_01.xlsx <https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.xlsx>`__

CLI
---

ExelCy has basic CLI command for execute:

.. code-block:: bash

    $ excelcy execute https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.xlsx


Data Definition
---------------

ExcelCy has data definition which expressed in `api.yml <https://github.com/kororo/excelcy/raw/master/data/api.yml>`__. As long as, data given in this specific format and structure, ExcelCy will able to support any type of data format. Check out, the Excel file format in `api.xlsx <https://github.com/kororo/excelcy/raw/master/data/api.xlsx>`__. Data classes are defined with `attrs <https://github.com/python-attrs/attrs>`__, check in `storage.py <https://github.com/kororo/excelcy/raw/master/excelcy/storage.py>`__ for more detail.


TODO
----

- [X] Start get cracking into spaCy

- [ ] More features and enhancements listed `here <https://github.com/kororo/excelcy/labels/enhancement>`__

    - [ ] [`link <https://github.com/kororo/excelcy/issues/5>`__] JSONL integration with Prodigy
    - [ ] [`link <https://github.com/kororo/excelcy/issues/7>`__] Add logging and the settings
    - [ ] Add special case for tokenisation described `here <https://spacy.io/usage/linguistic-features#special-cases>`__
    - [ ] Add custom tags.
    - [ ] Add classifier text training described `here <https://spacy.io/usage/training#textcat>`__
    - [ ] Add exception subtext when there is multiple occurrence in text. (Google Pay is awesome Google product)
    - [ ] Add tag annotation in sheet: train
    - [ ] Add ref in data storage
    - [ ] Improve speed and performance
    - [X] Add list of patterns easily (such as kitten breed.
    - [X] Add more data structure check in Excel and more warning messages
    - [X] Add plugin, otherwise just extends for now.
    - [X] [`link <https://github.com/kororo/excelcy/issues/6>`__] Add enabled, notes columns
    - [X] [`link <https://github.com/kororo/excelcy/issues/4>`__] Add export outputs such as identified Entities, Tags
    - [X] [`link <https://github.com/kororo/excelcy/issues/3>`__] Add CLI support
    - [X] [`link <https://github.com/kororo/excelcy/issues/2>`__] Improve experience
    - [X] [`link <https://github.com/kororo/excelcy/issues/1>`__] Add more file format such as YML, JSON. Make standardise and well documented on data structure.
    - [X] Add support to accept sentences to Excel


- [X] Submit to Prodigy Universe

FAQ
---

**What is that idx columns in the Excel sheet?**

The idea is to give reference between two things. Imagine in sheet "train", like to know where the sentence generated from in sheet "source". And also, the nature of Excel, you can sort things, this is the safe guard to keep things in the correct order.

**Can ExcelCy import/export to X, Y, Z data format?**

ExcelCy has strong and well-defined data storage, thanks to `attrs <https://github.com/python-attrs/attrs>`__. It is possible to import/export data in any format.

**ExcelCy accepts suggestions/ideas?**

Yes! Please submit them into new issue with label "enhancement".

Acknowledgement
---------------

This project uses other awesome projects:

- `attrs <https://github.com/python-attrs/attrs>`__: Python Classes Without Boilerplate.
- `pyexcel <https://github.com/pyexcel/pyexcel>`__: Single API for reading, manipulating and writing data in csv, ods, xls, xlsx and xlsm files.
- `pyyaml <https://github.com/yaml/pyyaml>`__: The next generation YAML parser and emitter for Python.
- `spacy <https://github.com/explosion/spaCy>`__: Industrial-strength Natural Language Processing (NLP) with Python and Cython.
- `textract <https://github.com/deanmalmgren/textract>`__: extract text from any document. no muss. no fuss.
