import os
import random
import spacy
from excelcy import utils
from excelcy.errors import Errors
from excelcy.pipe import MatcherPipe, EXCELCY_MATCHER
from excelcy.storage import Storage, Source, Prepare, Train
from excelcy.utils import odict


class ExcelCy(object):
    def __init__(self, storage_cls=None):
        storage_cls = storage_cls or Storage
        self.storage = storage_cls()  # type: Storage
        self._nlp = None

    @classmethod
    def execute(cls, file_path: str):
        excelcy = cls()
        excelcy.load(file_path=file_path)

        # prepare the phases
        phases = excelcy.storage.phase
        if len(phases.items) == 0:
            # get default phases
            for fn in ['discover', 'prepare', 'train', 'save_nlp']:
                phases.add(fn=fn)

        # execute the fns
        for idx, phase in excelcy.storage.phase.items.items():
            if phase.enabled:
                fno = getattr(excelcy, phase.fn)
                fno(**phase.args)

        return excelcy

    @property
    def nlp(self):
        if not self._nlp:
            self._nlp = self.create_nlp()
        return self._nlp

    def resolve_path(self, file_path: str = None):
        if file_path:
            file_path = self.storage.resolve_value(value=file_path)
            return os.path.join(self.storage.base_path, file_path)
        return None

    def resolve_ensure_path(self, file_path: str = None):
        file_path = self.resolve_path(file_path=file_path)
        if file_path:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return file_path

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

    def save_storage(self, file_path: str = None):
        self.storage.save(file_path=file_path)
        return self

    def save_nlp(self, file_path: str = None):
        nlp = self.nlp

        # remove the pipe because it is not useful for other purposes rather than learning
        if EXCELCY_MATCHER in nlp.pipe_names:
            nlp.remove_pipe(EXCELCY_MATCHER)

        # parse and ensure path
        file_path = file_path or self.storage.nlp_path
        file_path = self.resolve_ensure_path(file_path=file_path)

        # save the model
        if file_path:
            nlp.to_disk(file_path)

    def create_nlp(self):
        """
        Get NLP object with NER pipe enabled

        :return: NLP object
        """

        # parse path and ensure exists
        self.storage.nlp_path = self.resolve_ensure_path(file_path=self.storage.config.nlp_name)

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

    def _discover_prodigy(self, source: Source):
        """
        Apply Prodigy dataset, described  here
        :param source:
        :return:
        """

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

    def _prepare_init_file(self, prepare: Prepare):
        wb = utils.excel_load(file_path=self.resolve_path(prepare.value))
        for item in wb.get('prepare', []):
            prepare = Prepare.make(items=item)
            self._prepare_init_base(prepare=prepare)

    def _prepare_parse(self, train: Train):
        # parsing pre-identified Entity based on current data model
        doc = self.nlp(train.text)
        for ent in doc.ents:
            subtext, offset, label = ent.text, '%s,%s' % (ent.start_char, ent.end_char), ent.label_
            train.add(subtext=subtext, offset=offset, entity=label)

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
                # ensure offset is valid positions
                if not gold.offset:
                    offset = train.text.find(gold.subtext)
                    if offset != -1:
                        gold.offset = '%s,%s' % (offset, offset + len(gold.subtext))
                offset = gold.offset.replace(' ', '').strip()
                if not entities.get(offset):
                    entities[offset] = gold.entity
            trains[idx] = {'entities': []}
            for offset, entity in entities.items():
                offsets = offset.split(',')
                trains[idx]['entities'].append([int(offsets[0]), int(offsets[1]), entity])

        # train now
        nlp.vocab.vectors.name = 'spacy_pretrained_vectors'
        optimizer = nlp.begin_training()
        for itn in range(self.storage.config.train_iteration):
            random.shuffle(train_idx)
            for idx in train_idx:
                text = self.storage.train.items[idx].text
                train = trains[idx]
                nlp.update([text], [train], drop=self.storage.config.train_drop, sgd=optimizer)

        return self

    def retest(self):
        for idx, train in self.storage.train.items.items():
            # clear before retest the entities
            train.items = odict()
            # it is the same concept as prepare
            self._prepare_parse(train=train)

    def export_train(self, file_path: str):
        self.storage.save(file_path=self.resolve_ensure_path(file_path), kind=['train'])
