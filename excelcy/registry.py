import collections
import attr


field = attr.ib


@attr.s
class Registry(object):
    @classmethod
    def field_names(cls):
        names = [field.name for field in attr.fields(cls)]
        return names

    @classmethod
    def __registry__filter_items(cls, items: dict) -> dict:
        """
        Filtered items based on the given class attrs
        :param item: Data in dictionary
        :return: Filtered data in dictionary
        """
        names = cls.field_names()
        validated_items = {k: items.get(k) for k in set(names).intersection(set(items.keys()))}
        return validated_items

    @classmethod
    def make(cls, items: dict):
        filtered_items = cls.__registry__filter_items(items=items)
        # noinspection PyArgumentList
        inst = cls(**filtered_items)
        return inst

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
        filtered_items = self.__registry__filter_items(items=items)
        for k, v in filtered_items.items():
            object.__setattr__(self, k, v)
        return self

    def as_dict(self) -> dict:
        data = attr.asdict(self, dict_factory=collections.OrderedDict)
        return data

    def validate(self):
        return attr.validate(self)
