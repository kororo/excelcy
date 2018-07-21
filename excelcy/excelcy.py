import os
import random
import tempfile
import typing
import spacy
from excelcy.pipe import MatcherPipe, EXCELCY_MATCHER
from excelcy.storage import Storage, Source
from excelcy.utils import odict
from excelcy.errors import Errors


class DataTrainer(object):
    def __init__(self, data_path: str, options: dict = None):
        """
        SpaCy data trainer with Excel.

        The test data can be obtained in directory "tests/files/data1.xlsx"
        It was taken from https://spacy.io/usage/training#training-data

        See link: https://spacy.io/usage/training

        Options:
        - clean: Delete existing model

        :param data_path: The excel path.
        :param options: The options allowed.
        """
        options = options or {}
        options.update(options)
        self.options = options

        # nlp model path
        self.nlp_path = None
        self.data_init = False
        self.data_path = None
        self.data_train = odict()  # type: typing.Dict[str, odict]
        self.data_pipes = odict()
        self.data_config = odict()

        # load the data from given path
        self.data_load(data_path=data_path)

        # prepare the nlp object
        self.nlp = self.create_nlp()

    def reset(self):
        self.nlp_path = None
        self.data_init = False
        self.data_path = None
        self.data_train = odict()  # type: typing.Dict[str, odict]
        self.data_pipes = odict()
        self.data_config = odict()
        self.nlp = None

    def load_source(self, source_path: str):
        pass

    def _add_entities(self, ner):
        entities = []

        for _, data_instance in self.data_train.items():
            for _, _, entity in data_instance.get('gold', {}).get('entities', []):
                entities.append(entity)

        for data_pattern in self.data_pipes['matcher']:
            entity = data_pattern.get('entity')
            entities.append(entity)

        # https://spacy.io/usage/training#example-new-entity-type
        for entity in set(entities):
            ner.add_label(entity)

    def _train_matcher(self):
        # add matcher pipe
        nlp = self.nlp
        nlp.add_pipe(MatcherPipe(nlp, self.data_pipes['matcher']))

        # parse train data
        for _, data_instance in self.data_train.items():
            text = data_instance.get('text')
            doc = nlp(text)
            for ent in doc.ents:
                subtext, start, end, label = ent.text, ent.start_char, ent.end_char, ent.label_
                entity = [int(start), int(end), label]
                # insert at the begining so it is possible to be overriden
                data_instance['gold']['entities'].insert(0, entity)

    def train(self, auto_save: bool = True):
        if not self.data_init:
            # ensure data loaded
            raise ValueError(Errors.E001)

        # prepare nlp
        nlp = self.nlp
        ner = nlp.get_pipe('ner')

        # add all entity labels
        self._add_entities(ner=ner)

        # prepare config
        train_iteration, train_drop = self.data_config.get('train.iteration'), self.data_config.get('train.drop')
        train_matcher = self.data_config.get('train.matcher')

        if train_matcher is True:
            # been told to auto add Entity based on the rule based matching
            self._train_matcher()

        # prepare data
        data_train_key = list(self.data_train.keys())

        # train now
        nlp.vocab.vectors.name = 'spacy_pretrained_vectors'
        optimizer = nlp.begin_training()
        for itn in range(train_iteration):
            random.shuffle(data_train_key)
            for key in data_train_key:
                data_instance = self.data_train[key]
                gold = data_instance.get('gold')
                if gold:
                    text = data_instance.get('text')
                    nlp.update([text], [gold], drop=train_drop, sgd=optimizer)

        # test, parse and update data
        data_train_key = list(self.data_train.keys())
        for key in data_train_key:
            data_instance = self.data_train[key]
            text = data_instance.get('text')
            subtext = odict()  # type: dict
            doc = nlp(text)
            for idx, token in enumerate(doc):
                skey = '%s.%s' % (key, idx)
                subtext[skey] = subtext.get(idx, odict())
                subtext[skey]['subtext'] = token.text
                subtext[skey]['span'] = '%s,%s' % (token.idx, token.idx + len(token.text))
                subtext[skey]['entity'] = token.ent_type_
                subtext[skey]['tag'] = token.tag_
            data_instance['tokens'] = subtext

        # save
        if auto_save:
            if EXCELCY_MATCHER in nlp.pipe_names:
                nlp.remove_pipe(EXCELCY_MATCHER)
            nlp.to_disk(self.nlp_path)


class ExcelCy(object):
    def __init__(self):
        self.storage = Storage()
        self._nlp = None

    @property
    def nlp(self):
        if not self._nlp:
            self._nlp = self.create_nlp()
        return self._nlp

    def load(self, file_path: str):
        """
        Parse the file storage and load into memory
        :param file_path: The file path
        """
        self.storage.load(file_path=file_path)

    def save(self, file_path: str):
        self.storage.save(file_path=file_path)

    def resolve_path(self, file_path: str):
        tmp_path = os.environ.get('EXCELCY_TEMP_PATH', tempfile.gettempdir())
        file_path = file_path.replace('[tmp]', tmp_path)
        return os.path.join(self.storage.base_path, file_path)

    def create_nlp(self):
        """
        Get NLP object with NER pipe enabled

        :return: NLP object
        """
        # parse path and ensure exists
        self.storage.nlp_path = self.resolve_path(file_path=self.storage.config.nlp_name)
        os.makedirs(os.path.dirname(self.storage.nlp_path), exist_ok=True)

        try:
            # load NLP object with custom path to be loaded first, if fails, get the base which is lang code from spaCy.
            nlp = spacy.load(name=self.storage.nlp_path)
        except IOError:
            nlp = spacy.load(name=self.storage.config.nlp_base)
            nlp.to_disk(self.storage.nlp_path)
            nlp = spacy.load(name=self.storage.nlp_path)
        return nlp

    def _discover_text(self, source: Source):
        """
        Apply Sentence Boundary Detection, described here https://spacy.io/usage/linguistic-features#sbd
        :param source: The source value with kind=text
        """
        # this is based on SBD described here
        doc = self.nlp(source.value)
        for sentence in doc.sents:
            # TODO: would be good to add ref from source
            self.storage.train.add(text=sentence)

    def _discover_textract(self, source: Source):
        """
        Apply textract parsing, described here http://textract.readthedocs.io/en/stable/
        :param source: The source value with kind=textract
        """
        # TODO: add textract check
        import textract
        # process it
        text = textract.process(self.resolve_path(file_path=source.value), language=self.storage.config.source_language)
        # create new source and pass it to text processor
        new_source = Source(idx=source.idx, kind='text', value=str(text))
        self._discover_text(new_source)

    def discover(self):
        """
        Start load source data, iterate one by one and parse into sentences
        :return:
        """
        for _, source in self.storage.source.items.items():
            processor = getattr(self, '_discover_%s' % source.kind)
            if processor:
                processor(source=source)

    def train(self, data_path: str, auto_save: bool = True, options: dict = None):
        data_trainer = DataTrainer(data_path=data_path, options=options)
        data_trainer.train(auto_save=auto_save)
