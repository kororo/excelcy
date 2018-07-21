from collections import OrderedDict as odict


def arrtodict(rows):
    vals = []
    header = rows[0] if len(rows) > 0 else []
    rows = rows[1:]
    # start populate
    for y, row in enumerate(rows):
        val = odict()
        for x, col in enumerate(row):
            val[header[x]] = col
        vals.append(val)
    return vals


def filteritems(items):
    # remove all empty value in dict
    new_items = [{k: v for k, v in item.items() if v} for item in items]
    # remove all empty dict
    new_items = [item for item in new_items if len(item) > 0]
    return new_items


def excel_load(file_path: str):
    import pyexcel
    # load workbook
    wb = pyexcel.get_book_dict(file_name=file_path)
    for name, item in wb.items():
        # ensure from array to odict and filter empty values
        wb[name] = filteritems(arrtodict(item))
    return wb


def excel_save(sheets, file_path: str):
    import pyexcel
    pyexcel.save_book_as(bookdict=sheets, dest_file_name=file_path)


def yaml_load(file_path: str):
    import yaml
    from yaml.resolver import BaseResolver

    def ordered_load(stream, loader_cls):
        class OrderedLoader(loader_cls):
            pass

        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return odict(loader.construct_pairs(node))

        OrderedLoader.add_constructor(BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
        return yaml.load(stream, OrderedLoader)

    return ordered_load(open(file_path, 'r'), yaml.SafeLoader)


def yaml_save(data, file_path: str):
    import yaml

    # link: https://stackoverflow.com/a/16782282/469954
    def yaml_represent_odict(dumper, data):
        value = []
        for item_key, item_value in data.items():
            node_key = dumper.represent_data(item_key)
            node_value = dumper.represent_data(item_value)
            value.append((node_key, node_value))
        return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

    yaml.add_representer(odict, yaml_represent_odict)
    yaml.dump(data, open(file_path, 'w'))
