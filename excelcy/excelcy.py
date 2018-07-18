import os
import random
import re
import shutil
import typing
import spacy
from spacy.language import Language
from spacy.matcher import PhraseMatcher, Matcher
from spacy.tokens.doc import Doc
from excelcy import utils
from excelcy.utils import odict


EXCELCY_MATCHER = 'excelcy-matcher'


class MatcherPipe(object):
    name = EXCELCY_MATCHER

    def __init__(self, nlp, patterns: list = None):
        """
        SpaCy pipe to match Entity based on multiple patterns.

        Pattern examples:
        patterns = [
            {'pattern': 'amazon', 'type': 'nlp', 'entity': 'PRODUCT'},
            {'pattern': 'ama(.+)', 'type': 'regex', 'entity': 'PRODUCT'}
        ]

        :param nlp: The NLP object
        :param patterns: The matcher patterns
        """
        self.nlp = nlp
        self.phrase_matcher = PhraseMatcher(nlp.vocab)
        self.matcher = Matcher(nlp.vocab)

        # start add pattern
        self.add_patterns(patterns=patterns or [])

    def add_patterns(self, patterns: list):
        """
        Add pattern list into matcher algo.

        :param patterns: List of pattern
        """
        for pattern in patterns:
            ppattern, ptype, pentity = pattern.get('pattern'), pattern.get('type'), pattern.get('entity')
            self.add_pattern(pattern=ppattern, ptype=ptype, entity=pentity)

    def add_pattern(self, pattern, ptype: str, entity: str):
        """
        Add pattern into matcher algorithm. There are two different types:
        - nlp: This uses PhraseMatcher which described in https://spacy.io/usage/linguistic-features#adding-phrase-patterns
        - regex: This uses Matcher which described in https://spacy.io/usage/linguistic-features#regex

        :param pattern: Entity pattern matcher
        :param ptype: Pattern matcher type, either 'nlp', 'regex'
        :param entity: Entity to be matched
        """
        if ptype == 'nlp':
            self.phrase_matcher.add(entity, None, *[self.nlp(pattern)])
        elif ptype == 'regex':
            regex_flag = self.nlp.vocab.add_flag(lambda text: self.eval_regex(pattern=pattern, text=text))
            self.matcher.add(entity, None, [{regex_flag: True}])

    def get_string_id(self, match_id: int):
        """
        Get string ID based on match ID.
        Example:
        - String ID: PRODUCT
        - Match ID: 123

        :param match_id: The match ID
        :return: The string ID
        """
        string_id = self.nlp.vocab.strings[match_id]
        return string_id

    def eval_regex(self, pattern, text):
        return bool(re.compile(pattern).match(text))

    def __call__(self, doc: Doc):
        """
        The spacy pipeline caller
        :param doc: The Doc token.
        """

        # get matches
        phrase_matches = self.phrase_matcher(doc)
        matches = self.matcher(doc)

        # process them
        for match_id, start, end in phrase_matches + matches:
            # start add them into entities list
            entity = (match_id, start, end)
            doc.ents += (entity,)
        return doc


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
        self.data_path = data_path
        self.data_train = odict()  # type: typing.Dict[str, odict]
        self.data_pipes = odict()
        self.data_config = odict()

        # load the data from given path
        self.data_load(data_path=data_path)

        # prepare the nlp object
        self.nlp = self.create_nlp()

    def create_nlp(self):
        """
        Get NLP object with NER pipe enabled

        :return: NLP object
        """
        name = self.data_config.get('name')
        base = self.data_config.get('base')
        base_path = os.path.dirname(self.data_path)
        self.nlp_path = os.path.join(base_path, name)

        # load NLP object with custom path to be loaded first, if fails, get the base which is lang code from SpaCy
        try:
            nlp = spacy.load(name=self.nlp_path)
            if self.options.get('clean') is True:
                # just to be safe, load it first, if valid then we clean up and restart again
                if os.path.exists(self.nlp_path) and os.path.isdir(self.nlp_path):
                    shutil.rmtree(self.nlp_path)
                nlp = spacy.load(name=self.nlp_path)
        except IOError:
            nlp = spacy.load(name=base)
            nlp.to_disk(self.nlp_path)
            nlp = spacy.load(name=self.nlp_path)

        # ensure path is exist
        os.makedirs(self.nlp_path, exist_ok=True)

        # ensure ner pipe exists
        if 'ner' not in nlp.pipe_names:
            ner = nlp.create_pipe('ner')
            nlp.add_pipe(ner)
        return nlp

    def data_load(self, data_path: str):
        """
        Load data from given path. Currently just Excel format in XLSX

        :param data_path: Excel in XLSX path
        """
        # parse data
        wb = utils.load_excel(data_path=data_path)
        # parse config
        for config in wb.get('config', odict()):
            config_name, config_value = config.get('name'), config.get('value')
            self.data_config[config_name] = config_value
        # parse train data
        for row in wb.get('train', odict()):
            row_id, text = str(row.get('id')), row.get('text')
            token_id = None
            if '.' in row_id:
                row_id, token_id = row_id.split('.')
            if token_id is None:
                data_instance = odict()
                data_instance['text'] = row.get('text')
                data_instance['rows'] = []
                data_instance['gold'] = odict()
                data_instance['gold']['entities'] = []
                self.data_train[row_id] = data_instance
            else:
                parent_row = self.data_train[row_id]
                text = parent_row['text']
                subtext, span, entity = row.get('subtext'), row.get('span'), row.get('entity')
                if subtext and entity:
                    if span:
                        start, end = span.split(',')
                    else:
                        start = text.find(subtext)
                        end = start + len(subtext)
                    parent_row['rows'].append(row)
                    ent = [int(start), int(end), entity]
                    parent_row['gold']['entities'].append(ent)
        # parse pipe-matcher
        self.data_pipes['matcher'] = self.data_pipes.get('matcher', [])
        for matcher in wb.get('pipe-matcher', []):
            self.data_pipes['matcher'].append(matcher)

    def data_save(self, data_path: str):
        sheets = odict()
        # TODO: refactor this
        sheets['train'] = [['id', 'text', 'config', 'subtext', 'span', 'entity', 'tag']]
        sheets['config'] = [['name', 'value']]

        # build config sheet
        for config_name, config_value in self.data_config.items():
            sheets['config'].append([config_name, config_value])

        # build train sheet
        for train_id, data_instance in self.data_train.items():
            row = [train_id, data_instance.get('text'), '']
            sheets['train'].append(row)

            tokens = data_instance['tokens']
            # check if there is tokens
            if tokens:
                for token_id, token in tokens.items():
                    row = [token_id, '', '']
                    # TODO: refactor this
                    for key in ['subtext', 'span', 'entity', 'tag']:
                        row.append(token.get(key))
                    sheets['train'].append(row)
        utils.save_excel(sheets=sheets, data_path=data_path)

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

    def train_matcher(self, auto_save: bool = True):
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
                data_instance['gold']['entities'].append(entity)

        # save
        if auto_save and False:
            self.data_save(data_path=self.data_path)

    def train(self, auto_save: bool = True):
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
            self.train_matcher(auto_save=auto_save)

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
            nlp.remove_pipe(EXCELCY_MATCHER)
            nlp.to_disk(self.nlp_path)


class ExcelCy(object):
    def __init__(self):
        """
        Helper class to utilise the library.
        """
        pass

    def train(self, data_path: str, auto_save: bool = True, options: dict = None):
        data_trainer = DataTrainer(data_path=data_path, options=options)
        data_trainer.train(auto_save=auto_save)


# add factories
Language.factories[EXCELCY_MATCHER] = lambda nlp, **cfg: MatcherPipe(nlp, **cfg)
