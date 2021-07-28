import numpy as np
import xml.etree.ElementTree as ET
import csv


def fetch_table_from_excel(classifier_fname):
    '''
    (deprecated)

    Given a path to an excel spreadsheet, returns a dictionary linking classification names to
    MEI snippets, given that it contains a table with columns labeled "mei" and "classification."
    '''
    from xlrd import open_workbook
    from unidecode import unidecode

    name_col = u'Encoding classifier'
    mei_col = u'Encoding MEI'
    wb = open_workbook(classifier_fname)
    sheet = wb.sheets()[0]

    for n in range(sheet.nrows):
        row = [x.value for x in sheet.row(n)]
        if name_col in row and mei_col in row:
            name_pos = row.index(name_col)
            mei_pos = row.index(mei_col)
            starting_from = n
            break

    name_to_mei = {}
    for n in range(starting_from + 1, sheet.nrows):
        item_name = sheet.cell(n, name_pos).value
        item_mei = sheet.cell(n, mei_pos).value
        item_mei = unidecode(item_mei)
        if not item_name:
            continue
        try:
            parsed = ET.fromstring(item_mei)
        except ET.ParseError:
            print('{} failed: row {}, col {}'.format(item_name, n, mei_pos))
            continue
        name_to_mei[item_name] = parsed
    return name_to_mei


def fetch_table_from_csv(fname):
    '''
    Given a path to a .csv file that was output from the MEI mapping tool,
    (github.com/DDMAL/mei-mapping-tool)
    outputs a dictionary linking classifications of glyphs (e.g., podatus2, punctum, ligature3)
    to ElementTree objects of MEI snippets.
    '''
    with open(fname, 'r') as f:
        table_reader = csv.reader(f)
        full_table = []
        for row in table_reader:
            full_table.append(row)
    header = full_table[0]
    mei_index = header.index('mei')
    class_index = header.index('classification')
    name_to_mei = {}
    for row in full_table[1:]:
        raw_xml = row[mei_index]
        class_name = row[class_index]
        try:
            parsed = ET.fromstring(raw_xml)
        except ET.ParseError:
            print('{} failed: xml {}'.format(class_name, raw_xml))
            continue
        name_to_mei[class_name] = parsed

    return name_to_mei
