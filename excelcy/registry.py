import collections
import attr


REGISTRY_METADATA_LABEL = 'label'
REGISTRY_METADATA_DESC = 'desc'
REGISTRY_METADATA_VISIBLE = 'visible'
REGISTRY_DATA = '__registry__data'
REGISTRY_FNS = '__registry__fns'


def field(default=attr.NOTHING, label: str = None, desc: str = None, visible: bool = True, validator=None, repr=True,
          cmp=True, hash=None, init=True, convert=None, metadata: dict = None):
    metadata = metadata if metadata else {}
    metadata[REGISTRY_METADATA_LABEL] = label
    metadata[REGISTRY_METADATA_DESC] = desc
    metadata[REGISTRY_METADATA_VISIBLE] = visible
    return attr.ib(default, validator, repr, cmp, hash, init, convert, metadata)


@attr.s
class Registry(object):
    def __getattribute__(self, item):
        try:
            item = super(Registry, self).__getattribute__(item)
            return item
        except AttributeError:
            return None

    def __setattr__(self, key, value):
        super(Registry, self).__setattr__(key, value)
        fns = getattr(self, REGISTRY_FNS)
        for fn in fns if fns else []:
            fn(k=key, v=value)

    def __attrs_post_init__(self):
        # check whether it is created using @attr.s
        if not self.__registry__is_init__():
            raise TypeError('"%s" missing @attr.s decorator' % self.__class__)
        object.__setattr__(self, REGISTRY_FNS, [])

    @classmethod
    def __registry__field_names(cls):
        names = [field.name for field in attr.fields(cls)]
        return names

    @classmethod
    def make(cls, data: dict):
        r = cls().extend(data)
        return r

    def __registry__is_init__(self):
        cls = self.__class__
        cls_dict = cls.__dict__
        init_by_attr_s = cls_dict.get('__attrs_attrs__') is not None
        return init_by_attr_s

    def __registry__get_data(self):
        try:
            __registry__data = object.__getattribute__(self, REGISTRY_DATA)
            return __registry__data
        except Exception:
            return {}

    def __registry__set_data(self, k, v):
        __registry__data = self.__registry__get_data()
        if isinstance(__registry__data, dict):
            __registry__data[k] = v

    def __registry__get_fns(self):
        __registry__fns = object.__getattribute__(self, REGISTRY_FNS)
        return __registry__fns

    def __registry__add_fn(self, fn):
        self.__registry__get_fns().append(fn)

    def extend(self, items: dict):
        items = items if items else {}
        for k, v in items.items():
            object.__setattr__(self, k, v)
        return self

    def items(self):
        data = self.__registry__get_data()
        data_update = attr.asdict(self, dict_factory=collections.OrderedDict)
        for k, v in data_update.items():
            data[k] = v
        return data

    def validate(self):
        return attr.validate(self)
