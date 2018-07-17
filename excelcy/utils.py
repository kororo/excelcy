import pyexcel
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


def load_excel(data_path):
    # load workbook
    wb = pyexcel.get_book_dict(file_name=data_path)
    for name, item in wb.items():
        # ensure from array to odict and filter empty values
        wb[name] = filteritems(arrtodict(item))
    return wb


def save_excel(sheets, data_path):
    pyexcel.save_book_as(bookdict=sheets, dest_file_name=data_path)
