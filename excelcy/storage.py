import copy
import datetime
import os
import tempfile
import typing
import attr
from excelcy import utils
from excelcy.registry import Registry, field
from excelcy.utils import odict


@attr.s
class BaseItemRegistry(Registry):
    """
    Base class for all item alike data
    """
    idx = field(default=None)  # type: int
    enabled = field(default=True)  # type: bool
    notes = field(default=None)  # type: str


@attr.s
class BaseItemListRegistry(Registry):
    """
    Base class for all list item alike data
    """
    items = field(default=attr.Factory(odict))  # type: typing.Dict[str, Registry]

    def add_item(self, item):
        item.idx = len(self.items) + 1 if not item.idx or item.idx == str(None) else item.idx
        self.items[str(item.idx)] = item
        return item


@attr.s()
class Config(Registry):
    """
    Storage for config in ExcelCy
    """
    nlp_base = field(default=None)  # type: str
    nlp_name = field(default=None)  # type: str
    source_language = field(default='en')  # type: str
    prepare_enabled = field(default=True)  # type: bool
    train_iteration = field(default=None)  # type: int
    train_drop = field(default=None)  # type: float


@attr.s()
class Phase(BaseItemRegistry):
    fn = field(default=None)  # type: str
    args = field(default=attr.Factory(odict))  # type: dict


@attr.s()
class Phases(BaseItemListRegistry):
    items = field(default=attr.Factory(odict))  # type: typing.Dict[str, Phase]

    def add(self, fn: str, args: dict = None, idx: str = None):
        item = Phase(fn=fn, args=args or odict(), idx=str(idx))
        self.add_item(item=item)
        return item


@attr.s()
class Source(BaseItemRegistry):
    kind = field(default=None)  # type: str
    value = field(default=None)  # type: str


@attr.s()
class Sources(BaseItemListRegistry):
    def add(self, kind: str, value: str, idx: str = None):
        item = Source(kind=kind, value=value, idx=str(idx))
        self.add_item(item=item)
        return item


@attr.s()
class Prepare(BaseItemRegistry):
    kind = field(default=None)  # type: str
    value = field(default=None)
    entity = field(default=None)  # type: str


@attr.s()
class Prepares(BaseItemListRegistry):
    items = field(default=attr.Factory(odict))  # type: typing.Dict[str, Prepare]

    def add(self, kind: str, value, entity: str, idx: str = None):
        item = Prepare(kind=kind, value=value, entity=entity, idx=str(idx))
        self.add_item(item=item)
        return item


@attr.s()
class Gold(BaseItemRegistry):
    subtext = field(default=None)  # type: str
    offset = field(default=None)  # type: str
    entity = field(default=None)  # type: str


@attr.s()
class Train(BaseItemRegistry):
    text = field(default=None)  # type: str
    items = field(default=attr.Factory(odict))  # type: typing.Dict[str, Gold]

    def add(self, subtext: str, entity: str, offset: str = None, idx: str = None):
        item = Gold(subtext=subtext, offset=offset, entity=entity, idx=str(idx))
        self.add_item(item=item)
        return item

    def add_item(self, item: Gold):
        item.idx = '%s.%s' % (self.idx, len(self.items) + 1) if not item.idx or item.idx == str(None) else item.idx
        self.items[str(item.idx)] = item
        return item


@attr.s()
class Trains(BaseItemListRegistry):
    items = field(default=attr.Factory(odict))  # type: typing.Dict[str, Train]

    def add(self, text: str, idx: str = None):
        item = Train(text=text, idx=str(idx))
        self.add_item(item=item)
        return item


@attr.s()
class Storage(Registry):
    phase = field(default=attr.Factory(Phases))  # type: Phases
    source = field(default=attr.Factory(Sources))  # type: Sources
    prepare = field(default=attr.Factory(Prepares))  # type: Prepares
    train = field(default=attr.Factory(Trains))  # type: Trains
    config = field(default=attr.Factory(Config))  # type: Config

    def resolve_value(self, value: str):
        if type(value) == str:
            now = datetime.datetime.now()
            tmp_path = os.environ.get('EXCELCY_TEMP_PATH', tempfile.gettempdir())
            value = value.replace('[tmp]', tmp_path)
            if self.base_path:
                value = value.replace('[base_path]', self.base_path)
            if self.nlp_path:
                value = value.replace('[nlp_path]', self.nlp_path)
            if self.storage_path:
                value = value.replace('[storage_path]', self.storage_path)
            value = value.replace('[date]', now.strftime("%Y%m%d"))
            value = value.replace('[time]', now.strftime("%H%M%S"))
        return value

    def __attrs_post_init__(self):
        super(Storage, self).__attrs_post_init__()
        self.base_path = None
        self.nlp_path = None
        self.storage_path = None

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

        # parse phase
        data['phase'] = odict()
        data['phase']['items'] = odict()
        for phase in wb.get('phase', []):
            idx = phase.get('idx', len(data['phase']['items']))
            args = odict()
            raws = phase.get('args', '').split(',')
            for raw in raws:
                kv = raw.split('=')
                if len(kv) == 2:
                    key, value = kv
                    args[key.strip()] = value.strip()
            phase['args'] = args
            data['phase']['items'][str(idx)] = phase

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
                for k in ['idx', 'subtext', 'offset', 'entity']:
                    g[k] = train.get(k)
                t['items'][idx] = g

        # parse config
        data['config'] = odict()
        for config in wb.get('config', odict()):
            name, value = config.get('name'), config.get('value')
            data['config'][name] = value

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
            self.storage_path = file_path
        processor = getattr(self, '_load_%s' % file_ext[1:], None)
        if processor:
            processor(file_path=file_path)

    def _save_yml(self, file_path: str, kind: list):
        data = self.as_dict()
        names = list(data.keys())
        for name in names:
            if name not in kind:
                del data[name]
        utils.yaml_save(file_path=file_path, data=data)

    def _save_xlsx(self, file_path: str, kind: list):
        def convert(header: list, registry: Registry) -> list:
            return [getattr(registry, key, None) for key in header]

        sheets = odict()

        # build phase sheet
        if 'phase' in kind:
            headers = ['idx', 'enabled', 'fn', 'args', 'notes']
            sheets['phase'] = [headers]
            for _, phase in self.phase.items.items():
                val = convert(sheets['phase'][0], phase)
                val[headers.index('args')] = ', '.join(
                    ['%s=%s' % (k, v) for k, v in val[headers.index('args')].items()])
                sheets['phase'].append(val)

        # build source sheet
        if 'source' in kind:
            headers = ['idx', 'enabled', 'kind', 'value', 'notes']
            sheets['source'] = [headers]
            for _, source in self.source.items.items():
                sheets['source'].append(convert(sheets['source'][0], source))

        # build prepare sheet
        if 'prepare' in kind:
            headers = ['idx', 'enabled', 'kind', 'value', 'entity', 'notes']
            sheets['prepare'] = [headers]
            for _, prepare in self.prepare.items.items():
                sheets['prepare'].append(convert(sheets['prepare'][0], prepare))

        # build train sheet
        if 'train' in kind:
            headers = ['idx', 'enabled', 'text', 'subtext', 'entity', 'notes']
            sheets['train'] = [headers]
            for _, train in self.train.items.items():
                sheets['train'].append(convert(sheets['train'][0], train))
                for _, gold in train.items.items():
                    sheets['train'].append(convert(sheets['train'][0], gold))

        # build config sheet
        if 'config' in kind:
            headers = ['name', 'value']
            sheets['config'] = [headers]
            for config_name, config_value in self.config.as_dict().items():
                sheets['config'].append([config_name, config_value])

        # save
        utils.excel_save(sheets=sheets, file_path=file_path)

    def save(self, file_path: str, kind: list = None):
        kind = kind or ['phase', 'source', 'prepare', 'train', 'config']
        file_name, file_ext = os.path.splitext(file_path)
        processor = getattr(self, '_save_%s' % file_ext[1:], None)
        if processor:
            processor(file_path=file_path, kind=kind)

    def parse(self, data: odict):
        """
        Overwrite current state of storage with given data
        :param data: Data in ordereddict
        """

        # copy the data
        data = copy.deepcopy(data)

        # parse phase
        self.phase = Phases()
        for idx, item in data.get('phase', {}).get('items', {}).items():
            args = item.get('args', odict())
            for key, val in args.items():
                args[key] = self.resolve_value(value=val)
            phase = Phase.make(items=item)
            self.phase.add_item(item=phase)

        # parse source
        self.source = Sources()
        for idx, item in data.get('source', {}).get('items', {}).items():
            source = Source.make(items=item)
            self.source.add_item(item=source)

        # parse prepare
        self.prepare = Prepares()
        for idx, item in data.get('prepare', {}).get('items', {}).items():
            prepare = Prepare.make(items=item)
            self.prepare.add_item(item=prepare)

        # parse train
        self.train = Trains()
        for idx, train_item in data.get('train', {}).get('items', {}).items():
            train = Train.make(items=train_item)
            self.train.add_item(item=train)
            for idx2, gold_item in train_item.get('items', {}).items():
                gold = Gold.make(items=gold_item)
                train.add_item(item=gold)

        # parse config
        self.config = Config.make(items=data.get('config', {}))
