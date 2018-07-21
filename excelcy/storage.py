import os
import typing
import attr
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


@attr.s()
class Source(Registry):
    idx = field(None)  # type: str
    kind = field(None)  # type: str
    value = field(None)  # type: str


@attr.s()
class Sources(Registry):
    items = field(odict())  # type: typing.Dict[str, Source]

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
    items = field(odict())  # type: typing.Dict[str, Prepare]

    def add(self, kind: str, value, entity: str, idx: str = None):
        idx = idx or len(self.items)
        item = Prepare(kind=kind, value=value, entity=entity, idx=str(idx))
        self.items[str(idx)] = item
        return item


@attr.s()
class Gold(Registry):
    idx = field(None)  # type: str
    subtext = field(None)  # type: str
    span = field(None)  # type: (int, int)
    entity = field(None)  # type: str


@attr.s()
class Train(Registry):
    idx = field(None)  # type: str
    text = field(None)  # type: str
    items = field(odict())  # type: typing.Dict[str, Gold]

    def add(self, subtext: str, span: (int, int), entity: str, idx: str = None):
        idx = idx or '%s.%s' % (self.idx, len(self.items))
        item = Gold(subtext=subtext, span=span, entity=entity, idx=str(idx))
        self.items[str(idx)] = item
        return item


@attr.s()
class Trains(Registry):
    items = field(odict())  # type: typing.Dict[str, Train]

    def add(self, text: str, idx: str = None):
        idx = idx or len(self.items)
        item = Train(text=text, idx=str(idx))
        self.items[str(idx)] = item
        return item


@attr.s()
class Storage(Registry):
    config = field(Config())  # type: Config
    source = field(Sources())  # type: Sources
    prepare = field(Prepares())  # type: Prepares
    train = field(Trains())  # type: Trains

    def save(self, file_path: str):
        file_name, file_ext = os.path.splitext(file_path)
        if file_ext == '.xlsx':
            # TODO: implement
            pass
        elif file_ext == '.json':
            # TODO: implement
            pass
        else:
            # TODO: implement
            pass

    def load(self, file_path: str):
        file_name, file_ext = os.path.splitext(file_path)
        if file_ext == '.xlsx':
            # TODO: implement
            pass
        elif file_ext == '.json':
            # TODO: implement
            pass
        else:
            # TODO: implement
            pass

storage = Storage()
storage.source.items['1'].kind