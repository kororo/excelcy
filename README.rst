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

ExcelCy is a spaCy toolkit to help improving the data training experiences. ExcelCy is able to parse Word documents, PowerPoint presentations, PDF or images. Then, extract sentences from the files and train based on the given data in Excel file for compact data format.

ExcelCy is Powerful
-------------------

ExcelCy focuses on training spaCy data model. This is spaCy documentation from `Simple Style Training <https://spacy.io/usage/training#training-simple-style>`__.

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

The **TRAIN_DATA**, describes list of text sentences including the annotated entities to be trained. It is cumbersome to always count the characters. With ExcelCy, (start,end) characters can be omitted.

.. code-block:: python

    # use Excel data format for easier experience, this is API example.
    from excelcy import ExcelCy
    from excelcy.storage import Config

    # create object
    excelcy = ExcelCy()
    # set config
    excelcy.storage.config = Config(nlp_base='en_core_web_sm', train_iteration=2, train_drop=0.2)
    # add training data
    train = excelcy.storage.train.add(text='Uber blew through $1 million a week')
    # assign Uber -> ORG
    train.add(subtext='Uber', entity='ORG')
    # train it
    excelcy.train()
    # test it
    assert excelcy.nlp('Uber blew through $1 million a week').ents[0].label_ == 'ORG'

It is tedious job to annotate "Uber" to "ORG" in multiple sentences. By using ExcelCy, can be addressed using regex or phrase matcher.

.. code-block:: python

    # use Excel data format for easier experience, this is API example.
    from excelcy import ExcelCy
    from excelcy.storage import Config

    # create object
    excelcy = ExcelCy()
    # set config
    excelcy.storage.config = Config(nlp_base='en_core_web_sm', train_iteration=2, train_drop=0.2)
    # add training data
    excelcy.storage.train.add(text='Robertus Johansyah is the maintainer ExcelCy')
    excelcy.storage.train.add(text='Who is the maintainer of ExcelCy? Robertus Johansyah, I think.')
    # add phrase matcher Robertus Johansyah -> PERSON
    excelcy.storage.prepare.add(kind='phrase', value='Robertus Johansyah', entity='PERSON')
    # automatically assign Robertus Johansyah -> PERSON into training data
    excelcy.prepare()
    # train it
    excelcy.train()
    # test it
    assert excelcy.nlp('Robertus Johansyah is maintainer ExcelCy').ents[0].label_ == 'PERSON'
    assert excelcy.nlp('Who is the maintainer of ExcelCy? Robertus Johansyah, I think.').ents[1].label_ == 'PERSON'

Installing `textract <https://github.com/deanmalmgren/textract>`__ enables ExcelCy to load sources from Word documents, PowerPoint presentations, PDF or images. This helps especially if there are lots of training data in different files.

.. code-block:: python

    # use Excel data format for easier experience, this is API example.
    from excelcy import ExcelCy
    from excelcy.storage import Config

    # create object
    excelcy = ExcelCy()
    # set config
    excelcy.storage.base_path = 'curernt_project_path'
    excelcy.storage.config = Config(nlp_base='en_core_web_sm', train_iteration=2, train_drop=0.2)
    # add sources
    excelcy.storage.source.add(kind='text', value='Robertus Johansyah is the maintainer ExcelCy')
    excelcy.storage.source.add(kind='textract', value='source/test_source_01.txt')
    # add phrase matcher Uber -> ORG and Robertus Johansyah -> PERSON
    excelcy.storage.prepare.add(kind='phrase', value='Uber', entity='ORG')
    excelcy.storage.prepare.add(kind='phrase', value='Robertus Johansyah', entity='PERSON')
    # parse data sources
    excelcy.discover()
    # automatically assign Uber -> ORG and Robertus Johansyah -> PERSON into training data
    excelcy.prepare()
    # train it
    excelcy.train()
    # test it
    assert excelcy.nlp('Uber blew through $1 million a week').ents[0].label_ == 'ORG'
    assert excelcy.nlp('Robertus Johansyah is maintainer ExcelCy').ents[0].label_ == 'PERSON'


ExcelCy is Friendly
-------------------

1. Discovery

This phase is to specify data sources, which also accept `textract <http://textract.readthedocs.io/en/latest/>`__.
The sources should be parsed and converted into sentences.

**Input -> Process -> Output:**
    Documents/Files or raw text -> textract/file parser -> sentences

More Information:

- Excel sheet, "source": `tests/data/test_data_01.xlsx <https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.xlsx>`__
- YML, field "source": `tests/data/test_data_01.yml <https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.yml>`__
- Function: ExcelCy.discover()

2. Preparation

Preparation phase is to further process the sentences from previous phase. The sentences are analysed with extra pipe called MatcherPipe, the process has same concept similar to meta-learning, which the current sentences are annotated with pre-identified words/patterns such as:

- Phrase pattern: Robertus Johansyah, Uber, Google, Amazon
- Regex pattern: time regex ^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$

And also, any identified entities based on current model added in this phase.

**Input -> Process -> Output:**
    Sentences -> Apply nlp(sentence) + MatcherPipe -> Identified list of Entity

More Information:
- Excel sheet, "prepare": `tests/data/test_data_01.xlsx <https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.xlsx>`__
- YML, field "prepare": `tests/data/test_data_01.yml <https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.yml>`__
- Function: ExcelCy.prepare()

3. Training

In this phase, User train current/new data model to improve the quality based on the specified list of Entities annotation.

**Input -> Process -> Output:**
    nlp data model -> NER training -> nlp data model

More Information:
- Excel sheet, "train": `tests/data/test_data_01.xlsx <https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.xlsx>`__
- YML, field "train": `tests/data/test_data_01.yml <https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.yml>`__

- Function: ExcelCy.train()

4. Consolidation

After trained, User able to save the result into disk. Potentially, keep repeat the steps.

ExcelCy is Comprehensive
------------------------

It is easy to inspect and understand what is the current state of the data in ExcelCy. In any phase of the training experience, it is possible to dump the values as Python objects or export it as Excel.

.. code-block:: python

    from excelcy import ExcelCy

    excelcy = ExcelCy()
    # load configuration from XLSX or YML or JSON
    # excelcy.load(file_path='test_data_01.xlsx')
    # or define manually
    excelcy.storage.config = Config(nlp_base='en_core_web_sm', train_iteration=2, train_drop=0.2)
    print(json.dumps(excelcy.storage.items(), indent=2))

    # add sources
    excelcy.storage.source.add(kind='text', value='Robertus Johansyah is the maintainer ExcelCy')
    excelcy.discover()
    print(json.dumps(excelcy.storage.items(), indent=2))

    # add phrase matcher Robertus Johansyah -> PERSON
    excelcy.storage.prepare.add(kind='phrase', value='Robertus Johansyah', entity='PERSON')
    excelcy.prepare()
    print(json.dumps(excelcy.storage.items(), indent=2))

    # train it
    excelcy.train()
    print(json.dumps(excelcy.storage.items(), indent=2))

    # test it
    doc = excelcy.nlp('Robertus Johansyah is maintainer ExcelCy')
    print(json.dumps(excelcy.storage.items(), indent=2))


ExcelCy is Growing
------------------

Currently, ExcelCy keeps improved. It is recommended to set fixed version in requirements.txt such as: "excelcy==0.2.0". The maintainers will keep minimum breaking changes. After major version 1.0.0, API will be locked and any breaking changes will be introduced first as deprecated and will be removed in the next major releases.

Features
--------

- Load multiple data sources such as Word documents, PowerPoint presentations, PDF or images.
- Import/Export configuration with JSON, YML or Excel.
- Add custom Entity labels.
- Annotate Entity from given sentences without (start, end) char position.
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

To train the SpaCy model:

.. code-block:: bash

    # ensure data model
    spacy download en

    # download example data
    wget https://github.com/kororo/excelcy/raw/master/tests/data/test_data_28.xlsx

.. code-block:: python

    from excelcy import ExcelCy
    excelcy = ExcelCy.execute(file_path='test_data_28.xlsx')

Note: `tests/data/test_data_28.xlsx <https://github.com/kororo/excelcy/raw/master/tests/data/test_data_28.xlsx>`__

Test the training manually:

.. code-block:: python

    import os
    import spacy
    import tempfile
    from excelcy import ExcelCy

    # create nlp data model based on "en_core_web_sm" and save it to "test_data_01"
    base = 'en_core_web_sm'
    nlp = spacy.load(base)

    # save and reload to verify

    # create dir nlp
    name = os.path.join(tempfile.gettempdir(), 'nlp/test_data_01')
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
    # copy excel from https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.xlsx
    # ensure name is "nlp/test_data_01" inside config sheet.
    # ensure directory data model "nlp/test_data_01" is created and exist.
    excelcy.train(data_path='tests/data/test_data_01.xlsx')

    # reload the data model
    nlp = spacy.load(name)

    # test the NER
    doc = nlp(text)
    ents = set([(ent.text, ent.label_) for ent in doc.ents])

    # this shows current model in test_data_01, has "Uber" identified as ORG
    assert ents == {('Uber', 'ORG'), ('$1 million', 'MONEY')}

Data Structure
--------------

ExcelCy has strong data definition which specified in `test_data_01.yml <https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.yml>`__. It is basically configuration of data dictionaries which enable ExcelCy to accept any type of configuration formats, such as, JSON, YML and Excel. ExcelCy uses `attrs <https://github.com/python-attrs/attrs>`__, which greatly help to add Code Intellisense of data storage.

Data Definition
---------------

config
^^^^^^

Extra configuration for the training.

- nlp_base: The initial SpaCy data model to begin with. Described in `here <https://spacy.io/models/>`__
- nlp_name: The absolute/relative path to save the SpaCy data model after training. It is possible to use this to read existing data model and training on top existing one. The path always relative to file.
- prepare_enabled: Enable to add entity annotation based on pipe-matcher, described below.
- train_iteration: How many iteration to train described `here <https://spacy.io/usage/training#annotations>`__
- train_drop: How much to dropout rate based on `here <https://spacy.io/usage/training#tips-dropout>`__

source
^^^^^^

Data source to train.

- idx: Unique ID
- kind: Data source type either "text" or "textract"
- value: The raw sentence if text, otherwise relative/absolute path to file

train
^^^^^

List of text sentences to train. This includes list of subtext to annotate any identified Entity.
Any non-existence Entity in nlp, it will automatically added using "ner" pipe, similar to
`here <https://spacy.io/usage/training#example-new-entity-type>`__.

- id: It follow format of "TEXT_ID.SUBTEXT_ID"
- text: The text sentence to train
- subtext: The portion of text to annotate the Entity
- entity: The label Entity, this can be existing or new label.


**Notes:**

- "text" and "subtext" needs to be case-sensitive.
- "subtext" is not affected by the tokenisation. It is possible to annotate multiple tokens for an Entity label.


**Examples:**

- `tests/data/test_data_01.xlsx <https://github.com/kororo/excelcy/raw/master/tests/data/test_data_01.xlsx>`__

Sheet: pipe-matcher
^^^^^^^^^^^^^^^^^^^

This list helps if there are lots of subtext occurrence in "train" sheet.

If type is "nlp":

- pattern: The exact phrase match to select subtext
- type: nlp
- entity: The annotated Entity label


If type is "regex":

- pattern: The regex to select subtext
- type: regex
- entity: The annotated Entity label


**Examples:**

- {'pattern': '$1 million', 'type': 'nlp', 'entity': 'MONEY'}
- {'pattern': 'Ubers?', 'type': 'regex', 'entity': 'ORG'}


TODO
----

- [X] Start get cracking into spaCy

- [ ] More features and enhancements listed `here <https://github.com/kororo/excelcy/labels/enhancement>`__

    - [ ] [`link <https://github.com/kororo/excelcy/issues/2>`__] Improve experience
    - [ ] [`link <https://github.com/kororo/excelcy/issues/1>`__] Add more file format such as YML, JSON. Make standardise and well documented on data structure.
    - [ ] Add special case for tokenisation described `here <https://spacy.io/usage/linguistic-features#special-cases>`__
    - [ ] Add custom tags.
    - [ ] Add report outputs such as identified entity, tag
    - [ ] Add support to accept sentences to Excel
    - [ ] Add more data structure check in Excel and more warning messages
    - [ ] Add classifier text training described `here <https://spacy.io/usage/training#textcat>`__
    - [ ] Add exception subtext when there is multiple occurrence in text. (Google Pay is awesome Google product)
    - [ ] Add tag annotation in sheet: train
    - [ ] Add list of patterns easily (such as kitten breed)
    - [ ] Add ref in data storage
    - [ ] Add plugin, otherwise just extends for now

- [ ] Improve speed and performance
- [ ] 100% coverage target with config (branch=on)
- [X] Submit to Prodigy Universe

FAQ
---
1. Why there is requirement to add idx values in column?


Acknowledgement
---------------

This project uses other awesome projects:

- `attrs <https://github.com/python-attrs/attrs>`__: Python Classes Without Boilerplate
- `pyexcel <https://github.com/pyexcel/pyexcel>`__:
- `pyyaml <https://github.com/yaml/pyyaml>`__: The next generation YAML parser and emitter for Python.
- `spacy <https://github.com/explosion/spaCy>`__
- `textract <https://github.com/deanmalmgren/textract>`__