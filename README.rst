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

ExcelCy is a SpaCy toolkit to help improve the data training experiences. It provides easy annotation using Excel file format.
It has helper to pre-train entity annotation with phrase and regex matcher pipe.

ExcelCy is Powerful
-------------------

ExcelCy focuses on the needs of training data into spaCy data model. Illustration below is based on the documentation in
`Simple Style Training <https://spacy.io/usage/training#training-simple-style>`__.

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

The **TRAIN_DATA**, describes list of text sentences including the annotated entities to be trained. It is cumbersome
to always count the characters. With ExcelCy, start,end characters can be omitted.

.. code-block:: python

    # this is illustration presentation only, please use Excel for now which described below.
    self.data_train = {
        '1.0': {
            'text': 'Uber blew through $1 million a week',
            'rows': [{'subtext': 'Uber', 'entity': 'ORG'}]
        }
    }


Also, it is lots of task if there are multiple text sentences with Uber as subtext. With ExcelCy, there is another way
to automatically add the annotation Entity using pipe-matcher either exact match or regex.

.. code-block:: python

    # this is illustration presentation only, please use Excel for now which desribed below.
    self.data_train = {
        '1.0': {
            'text': 'Uber blew through $1 million a week',
            'rows': [{'subtext': 'Uber', 'entity': 'ORG'}]
        }
    }




Features
--------

- Add training data from Excel.
- Add custom Entity labels.
- Annotate Entity from given sentences without (start, end) char position.
- Rule based phrase matching using `PhraseMatcher <https://spacy.io/usage/linguistic-features#adding-phrase-patterns>`__
- Rule based matching using `regex + Matcher <https://spacy.io/usage/linguistic-features#regex>`__
- Add Entity training data using pipe matcher described above.

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
    wget https://github.com/kororo/excelcy/tree/master/excelcy/tests/data/test_data_28.xlsx

.. code-block:: python

    import os
    import tempfile
    import spacy
    from excelcy import ExcelCy

    excelcy = ExcelCy()
    excelcy.train(data_path='test_data_28.xlsx')

Note: `tests/data/test_data_28.xlsx <https://github.com/kororo/excelcy/tree/master/excelcy/tests/data/test_data_28.xlsx>`__

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
    # copy excel from https://github.com/kororo/excelcy/tree/master/excelcy/tests/data/test_data_01.xlsx
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

Data
----

Currently ExcelCy only support Excel format. The DataTrainer needs three pieces of information:

Sheet: config
^^^^^^^^^^^^^

Extra configuration for the training.

- base: The initial SpaCy data model to begin with. Described in `here <https://spacy.io/models/>`__
- name: The absolute/relative path to save the SpaCy data model after training. It is possible to use this to read existing data model and training on top existing one. The path always relative to file.
- train.iteration: How many iteration to train described `here <https://spacy.io/usage/training#annotations>`__
- train.drop: How much to dropout rate based on `here <https://spacy.io/usage/training#tips-dropout>`__
- train.matcher: Enable to add entity annotation based on pipe-matcher, described below.

Sheet: train
^^^^^^^^^^^^

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

- `tests/data/test_data_01.xlsx <https://github.com/kororo/excelcy/tree/master/excelcy/tests/data/test_data_01.xlsx>`__
- `tests/data/test_data_02.xlsx <https://github.com/kororo/excelcy/tree/master/excelcy/tests/data/test_data_02.xlsx>`__
- `tests/data/test_data_03.xlsx <https://github.com/kororo/excelcy/tree/master/excelcy/tests/data/test_data_03.xlsx>`__
- `tests/data/test_data_04.xlsx <https://github.com/kororo/excelcy/tree/master/excelcy/tests/data/test_data_04.xlsx>`__

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

- [ ] More features

    - [ ] Add special case for tokenisation described `here <https://spacy.io/usage/linguistic-features#special-cases>`__
    - [ ] Add more file format such as YML, JSON. Make standardise and well documented on data structure.
    - [ ] Add custom tags.
    - [ ] Add report outputs such as identified entity, tag
    - [ ] Add support to accept sentences to Excel
    - [ ] Add more data structure check in Excel and more warning messages
    - [ ] Add classifier text training described `here <https://spacy.io/usage/training#textcat>`__
    - [ ] Add exception subtext when there is multiple occurrence in text. (Google Pay is awesome Google product)
    - [ ] Add tag annotation in sheet: train
    - [ ] Add list of patterns easily (such as kitten breed)

- [ ] Improve speed and performance
- [ ] Create data standard
- [ ] 100% coverage target with branch on
- [ ] Submit to Prodigy Universe


Acknowledgement
---------------

This project uses other awesome projects:

- `spaCy <https://github.com/explosion/spaCy>`__
