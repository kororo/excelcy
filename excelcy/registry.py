import collections
import attr


field = attr.ib


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

    def __attrs_post_init__(self):
        # check whether it is created using @attr.s
        if not self.__registry__is_init__():
            raise TypeError('"%s" missing @attr.s decorator' % self.__class__)

    def __registry__is_init__(self):
        cls = self.__class__
        cls_dict = cls.__dict__
        init_by_attr_s = cls_dict.get('__attrs_attrs__') is not None
        return init_by_attr_s

    def extend(self, items: dict):
        items = items if items else {}
        for k, v in items.items():
            object.__setattr__(self, k, v)
        return self

    def items(self):
        data = attr.asdict(self, dict_factory=collections.OrderedDict)
        return data

    def validate(self):
        return attr.validate(self)
