import re
from spacy.language import Language
from spacy.matcher import PhraseMatcher, Matcher
from spacy.tokens import Span
from spacy.tokens.doc import Doc

EXCELCY_MATCHER = 'excelcy-matcher'


class MatcherPipe(object):
    name = EXCELCY_MATCHER

    def __init__(self, nlp, patterns: list = None):
        """
        SpaCy pipe to match Entity based on multiple patterns.

        Pattern examples:
        patterns = [
            {'kind': 'phrase', 'value': 'amazon', 'entity': 'PRODUCT'},
            {'kind': 'regex', 'value': 'ama(.+)', 'entity': 'PRODUCT'}
        ]

        :param nlp: The NLP object
        :param patterns: The matcher patterns
        """
        self.nlp = nlp
        self.phrase_matcher = PhraseMatcher(nlp.vocab)
        self.matcher = Matcher(nlp.vocab)

        self.extra_patterns = []
        # start add pattern
        self.add_patterns(patterns=patterns or [])

    def add_patterns(self, patterns: list):
        """
        Add pattern list into matcher algo.

        :param patterns: List of pattern
        """
        for pattern in patterns:
            kind, value, entity = pattern.get('kind'), pattern.get('value'), pattern.get('entity')
            self.add_pattern(kind=kind, value=value, entity=entity)

    def add_pattern(self, kind: str, value, entity: str):
        """
        Add pattern into matcher algorithm. There are two different types:
        - phrase: This uses PhraseMatcher which described in https://spacy.io/usage/linguistic-features#adding-phrase-patterns
        - regex: This uses Matcher which described in https://spacy.io/usage/linguistic-features#regex

        :param kind: Pattern matcher type, either 'phrase', 'regex'
        :param value: Entity pattern matcher
        :param entity: Entity to be matched
        """
        if kind == 'phrase':
            self.phrase_matcher.add(entity, None, *[self.nlp(value)])
        elif kind == 'regex':
            regex_flag = self.nlp.vocab.add_flag(lambda text: self.eval_regex(pattern=value, text=text))
            self.matcher.add(entity, None, [{regex_flag: True}])

    def eval_regex(self, pattern, text):
        return bool(re.compile(pattern).match(text))

    def _filter_spans(self, spans):
        # Filter a sequence of spans so they don't contain overlaps
        # For spaCy 2.1.4+: this function is available as spacy.util.filter_spans()
        def get_sort_key(span2):
            return span2.end - span2.start, -span2.start

        sorted_spans = sorted(spans, key=get_sort_key, reverse=True)
        result = []
        seen_tokens = set()
        for span in sorted_spans:
            # Check for end - 1 here because boundaries are inclusive
            if span.start not in seen_tokens and span.end - 1 not in seen_tokens:
                result.append(span)
            seen_tokens.update(range(span.start, span.end))
        result = sorted(result, key=lambda span: span.start)
        return result

    def __call__(self, doc: Doc):
        """
        The spacy pipeline caller
        :param doc: The Doc token.
        """

        # get matches
        phrase_matches = self.phrase_matcher(doc)
        matches = self.matcher(doc)

        # process them
        spans = []
        for match_id, start, end in phrase_matches + matches:
            # start add them into entities list
            span = Span(doc, start, end, label=match_id)
            spans.append(span)
        # print('Before', [(ent.label_, ent.text) for ent in doc.ents])
        doc.ents = self._filter_spans(spans + list(doc.ents))
        # print('After', [(ent.label_, ent.text) for ent in doc.ents])
        return doc


# add factories
Language.factories[EXCELCY_MATCHER] = lambda nlp, **cfg: MatcherPipe(nlp, **cfg)
