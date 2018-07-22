import os
import random
import tempfile
import spacy
from excelcy.errors import Errors
from excelcy.pipe import MatcherPipe, EXCELCY_MATCHER
from excelcy.storage import Storage, Source, Prepare, Train
from excelcy.utils import odict


class ExcelCy(object):
    def __init__(self):
        self.storage = Storage()
        self._nlp = None

    @classmethod
    def execute(cls, file_path: str):
        excelcy = cls()
        excelcy.load(file_path=file_path)
        excelcy.discover()
        excelcy.prepare()
        excelcy.train()
        return excelcy

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
        try:
            self.storage.load(file_path=file_path)
        except FileNotFoundError:
            raise ValueError(Errors.E001)
        return self

    def save(self, file_path: str):
        self.storage.save(file_path=file_path)
        return self

    def resolve_path(self, file_path: str = None):
        if file_path:
            tmp_path = os.environ.get('EXCELCY_TEMP_PATH', tempfile.gettempdir())
            file_path = file_path.replace('[tmp]', tmp_path)
            return os.path.join(self.storage.base_path, file_path)
        return None

    def create_nlp(self):
        """
        Get NLP object with NER pipe enabled

        :return: NLP object
        """
        # parse path and ensure exists
        self.storage.nlp_path = self.resolve_path(file_path=self.storage.config.nlp_name)
        if self.storage.nlp_path:
            os.makedirs(os.path.dirname(self.storage.nlp_path), exist_ok=True)

        try:
            # load NLP object with custom path to be loaded first, if fails, get the base which is lang code from spaCy.
            nlp = spacy.load(name=self.storage.nlp_path)
        except IOError:
            nlp = spacy.load(name=self.storage.config.nlp_base)
        return nlp

    def _discover_text(self, source: Source):
        """
        Apply Sentence Boundary Detection, described here https://spacy.io/usage/linguistic-features#sbd
        :param source: The source value with kind=text
        """
        # this is based on SBD described here
        doc = self.nlp(source.value)
        for sent in doc.sents:
            # TODO: would be good to add ref from source
            # TODO: add filter?
            text = sent.text.strip()
            self.storage.train.add(text=text)

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
        value = text.decode('utf-8')
        new_source = Source(idx=source.idx, kind='text', value=value)
        self._discover_text(new_source)

    def discover(self):
        """
        Start load source data, iterate one by one and parse into sentences
        """
        for _, source in self.storage.source.items.items():
            processor = getattr(self, '_discover_%s' % source.kind, None)
            if processor:
                processor(source=source)
        return self

    def _prepare_init_base(self, prepare: Prepare):
        pipe = self.nlp.get_pipe(EXCELCY_MATCHER)  # type: MatcherPipe
        pipe.add_pattern(kind=prepare.kind, value=prepare.value, entity=prepare.entity)

    def _prepare_init_phrase(self, prepare: Prepare):
        self._prepare_init_base(prepare=prepare)

    def _prepare_init_regex(self, prepare: Prepare):
        self._prepare_init_base(prepare=prepare)

    def _prepare_parse(self, train: Train):
        # parsing pre-identified Entity based on current data model
        doc = self.nlp(train.text)
        for ent in doc.ents:
            subtext, span, label = ent.text, '%s,%s' % (ent.start_char, ent.end_char), ent.label_
            train.add(subtext=subtext, span=span, entity=label)

    def prepare(self):
        """
        Identify Entity from sentences
        """
        if self.storage.config.prepare_enabled:
            # prepare nlp to add matcher pipe
            self.nlp.add_pipe(MatcherPipe(self.nlp))

            # parse data
            for _, prepare in self.storage.prepare.items.items():
                processor = getattr(self, '_prepare_init_%s' % prepare.kind, None)
                if processor:
                    processor(prepare=prepare)

            # identify sentences
            for _, train in self.storage.train.items.items():
                self._prepare_parse(train=train)
        return self

    def train(self):
        nlp = self.nlp

        # gather unique entities
        entities = []
        for _, train in self.storage.train.items.items():
            for _, gold in train.items.items():
                entities.append(gold.entity)

        # add custom entities based on https://spacy.io/usage/training#example-new-entity-type
        ner = nlp.get_pipe('ner')
        for entity in set(entities):
            ner.add_label(entity)

        # prepare data
        train_idx = list(self.storage.train.items.keys())
        trains = odict()
        for idx, train in self.storage.train.items.items():
            entities = odict()
            for gold_idx, gold in train.items.items():
                # ensure span is valid positions
                if not gold.span:
                    offset = train.text.find(gold.subtext)
                    if offset != -1:
                        gold.span = '%s,%s' % (offset, offset + len(gold.subtext))
                span = gold.span.replace(' ', '').strip()
                if not entities.get(span):
                    entities[span] = gold.entity
            trains[idx] = {'entities': []}
            for span, entity in entities.items():
                spans = span.split(',')
                trains[idx]['entities'].append([int(spans[0]), int(spans[1]), entity])

        # train now
        nlp.vocab.vectors.name = 'spacy_pretrained_vectors'
        optimizer = nlp.begin_training()
        for itn in range(self.storage.config.train_iteration):
            random.shuffle(train_idx)
            for idx in train_idx:
                text = self.storage.train.items[idx].text
                train = trains[idx]
                nlp.update([text], [train], drop=self.storage.config.train_drop, sgd=optimizer)

        # auto save if required and nlp_path is defined
        if self.storage.config.train_autosave and self.storage.nlp_path:
            if EXCELCY_MATCHER in nlp.pipe_names:
                nlp.remove_pipe(EXCELCY_MATCHER)
            nlp.to_disk(self.storage.nlp_path)

        return self
