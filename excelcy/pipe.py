import re
from excelcy.utils import odict
from spacy.language import Language
from spacy.matcher import PhraseMatcher, Matcher
from spacy.tokens.doc import Doc


EXCELCY_MATCHER = 'excelcy-matcher'


class MatcherPipe(object):
    class DataMatcherPipe(object):
        def __init__(self, data: odict):
            self.data = data

        @property
        def patterns(self):
            return self.data

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


# add factories
Language.factories[EXCELCY_MATCHER] = lambda nlp, **cfg: MatcherPipe(nlp, **cfg)
