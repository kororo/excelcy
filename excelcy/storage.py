import os
import typing
import attr
from excelcy import utils
from excelcy.registry import Registry, field
from excelcy.utils import odict


@attr.s()
class Config(Registry):
    """
    Storage for config in ExcelCy
    """
    nlp_base = field(None)  # type: str
    nlp_name = field(None)  # type: str
    source_language = field('en')  # type: str
    prepare_enabled = field(True)  # type: bool
    train_iteration = field(None)  # type: int
    train_drop = field(None)  # type: float
    train_autosave = field(False)  # type: bool


@attr.s()
class Source(Registry):
    idx = field(None)  # type: str
    kind = field(None)  # type: str
    value = field(None)  # type: str


@attr.s()
class Sources(Registry):
    items = field(None)  # type: typing.Dict[str, Source]

    def __attrs_post_init__(self):
        super(Sources, self).__attrs_post_init__()
        self.items = odict()

    def add(self, kind: str, value: str, idx: str = None):
        idx = idx or len(self.items)
        item = Source(kind=kind, value=value, idx=str(idx))
        self.items[str(idx)] = item
        return item


@attr.s()
class Prepare(Registry):
    idx = field(None)  # type: str
    kind = field(None)  # type: str
    value = field(None)
    entity = field(None)  # type: str


@attr.s()
class Prepares(Registry):
    items = field(lambda: None)  # type: typing.Dict[str, Prepare]

    def __attrs_post_init__(self):
        super(Prepares, self).__attrs_post_init__()
        self.items = odict()

    def add(self, kind: str, value, entity: str, idx: str = None):
        idx = idx or len(self.items)
        item = Prepare(kind=kind, value=value, entity=entity, idx=str(idx))
        self.items[str(idx)] = item
        return item


@attr.s()
class Gold(Registry):
    idx = field(None)  # type: str
    subtext = field(None)  # type: str
    span = field(None)  # type: str
    entity = field(None)  # type: str


@attr.s()
class Train(Registry):
    idx = field(None)  # type: str
    text = field(None)  # type: str
    items = field(None)  # type: typing.Dict[str, Gold]

    def __attrs_post_init__(self):
        super(Train, self).__attrs_post_init__()
        self.items = odict()

    def add(self, subtext: str, entity: str, span: str = None, idx: str = None):
        idx = idx or '%s.%s' % (self.idx, len(self.items))
        item = Gold(subtext=subtext, span=span, entity=entity, idx=str(idx))
        self.items[str(idx)] = item
        return item


@attr.s()
class Trains(Registry):
    items = field(None)  # type: typing.Dict[str, Train]

    def __attrs_post_init__(self):
        super(Trains, self).__attrs_post_init__()
        self.items = odict()

    def add(self, text: str, idx: str = None):
        idx = idx or len(self.items)
        item = Train(text=text, idx=str(idx))
        self.items[str(idx)] = item
        return item


@attr.s()
class Storage(Registry):
    config = field(None)  # type: Config
    source = field(None)  # type: Sources
    prepare = field(None)  # type: Prepares
    train = field(None)  # type: Trains

    def __attrs_post_init__(self):
        super(Storage, self).__attrs_post_init__()
        self.base_path = None
        self.nlp_path = None
        self.config = Config()
        self.source = Sources()
        self.prepare = Prepares()
        self.train = Trains()

    def _load_yml(self, file_path: str):
        """
        Data loader for YML
        :param file_path: YML file path
        """
        data = utils.yaml_load(file_path=file_path)
        self.parse(data=data)

    def _load_xlsx(self, file_path: str):
        """
        Data loader for XLSX, this needs to be converted back to YML structure format
        :param file_path: XLSX file path
        """
        wb = utils.excel_load(file_path=file_path)
        data = odict()

        # TODO: add validator, if wrong data input
        # TODO: refactor to less hardcoded?

        # parse config
        data['config'] = odict()
        for config in wb.get('config', odict()):
            name, value = config.get('name'), config.get('value')
            data['config'][name] = value

        # parse source
        data['source'] = odict()
        data['source']['items'] = odict()
        for source in wb.get('source', []):
            idx = source.get('idx', len(data['source']['items']))
            data['source']['items'][str(idx)] = source

        # parse prepare
        data['prepare'] = odict()
        data['prepare']['items'] = odict()
        for prepare in wb.get('prepare', []):
            idx = prepare.get('idx', len(data['prepare']['items']))
            data['prepare']['items'][str(idx)] = prepare

        # parse train
        data['train'] = odict()
        data['train']['items'] = odict()
        # lets ensure there is idx
        train_idx, gold_idx = 0, 0
        for train in wb.get('train', []):
            if train.get('text') is not None:
                if gold_idx > 0:
                    train_idx = train_idx + 1
                    gold_idx = 0
                if train.get('idx') is None:
                    train['idx'] = str(train_idx)
            else:
                if train.get('idx') is None:
                    train['idx'] = '%s.%s' % (train_idx, gold_idx)
                gold_idx = gold_idx + 1
        for train in wb.get('train', []):
            idx = str(train.get('idx'))
            train_idx, gold_idx = idx, None
            if '.' in idx:
                train_idx, gold_idx = idx.split('.')
            # add train list
            if train.get('text') is not None:
                t = odict()
                t['items'] = odict()
                for k in ['idx', 'text']:
                    t[k] = train.get(k)
                data['train']['items'][train_idx] = t
            else:
                t = data['train']['items'][train_idx]
                g = odict()
                for k in ['idx', 'subtext', 'span', 'entity']:
                    g[k] = train.get(k)
                t['items'][idx] = g
        self.parse(data=data)

    def load(self, file_path: str):
        """
        Load storage data from file path
        :param file_path: File path
        """

        # check whether it is remote URL
        if '://' in file_path:
            from urllib import request, parse
            import tempfile
            # download the file and put into temp dir
            file_url = file_path
            parsed = parse.urlparse(file_url)
            file_name, file_ext = os.path.splitext(os.path.basename(parsed.path))
            self.base_path = tempfile.gettempdir()
            file_path = os.path.join(self.base_path, file_name + file_ext)
            request.urlretrieve(file_url, file_path)
        else:
            # analyse the file name and ext
            file_name, file_ext = os.path.splitext(file_path)
            self.base_path = os.path.dirname(file_path)
        processor = getattr(self, '_load_%s' % file_ext[1:], None)
        if processor:
            processor(file_path=file_path)

    def _save_yml(self, file_path: str):
        utils.yaml_save(file_path=file_path, data=self.items())

    def _save_xlsx(self, file_path: str):
        def convert(header: list, registry: Registry):
            return [getattr(registry, key, None) for key in header]

        data = self.items()
        sheets = odict()

        # build source sheet
        headers = ['idx', 'kind', 'value']
        sheets['source'] = [headers]
        for _, source in self.source.items.items():
            sheets['source'].append(convert(sheets['source'][0], source))

        # build prepare sheet
        headers = ['idx', 'kind', 'value', 'entity']
        sheets['prepare'] = [headers]
        for _, prepare in self.prepare.items.items():
            sheets['prepare'].append(convert(sheets['prepare'][0], prepare))

        # build train sheet
        headers = ['idx', 'text', 'subtext', 'entity']
        sheets['train'] = [headers]
        for _, train in self.train.items.items():
            sheets['train'].append(convert(sheets['train'][0], train))
            for _, gold in train.items.items():
                sheets['train'].append(convert(sheets['train'][0], gold))

        # build config sheet
        headers = ['name', 'value']
        sheets['config'] = [headers]
        for config_name, config_value in self.config.items().items():
            sheets['config'].append([config_name, config_value])

        # save
        utils.excel_save(sheets=sheets, file_path=file_path)

    def save(self, file_path: str):
        file_name, file_ext = os.path.splitext(file_path)
        self.base_path = os.path.dirname(file_path)
        processor = getattr(self, '_save_%s' % file_ext[1:], None)
        if processor:
            processor(file_path=file_path)

    def parse(self, data: odict):
        """
        Overwrite current state of storage with given data
        :param data: Data in ordereddict
        """
        # parse config
        self.config = Config(**data.get('config', {}))

        # parse source
        self.source = Sources()
        for idx, source in data.get('source', {}).get('items', {}).items():
            self.source.add(**source)

        # parse prepare
        self.prepare = Prepares()
        for idx, prepare in data.get('prepare', {}).get('items', {}).items():
            self.prepare.add(**prepare)

        # parse train
        self.train = Trains()
        for idx, trn in data.get('train', {}).get('items', {}).items():
            train = self.train.add(idx=idx, text=trn.get('text'))
            for idx2, gold in trn.get('items', {}).items():
                train.add(**gold)
