# -*- coding: utf-8 -*-
import sys
 
# setting path
sys.path.append('..')

# To run this file, some imports in build_mei_file.py will need to be changed
# The correct ones for local development are there commented out
# Comment out the bad ones and uncomment the good ones

import build_mei_file as bm
import parse_classifier_table as pct
import json


def run_my_task(inputs, settings, outputs):

    jsomr_path = inputs['JSOMR'][0]['resource_path']
    with open(jsomr_path, 'r') as file:
        jsomr = json.loads(file.read())

    if 'Column Splitting Data' in inputs:
        split_ranges_path = inputs['Column Splitting Data'][0]['resource_path']
        with open(split_ranges_path, 'r') as file:
            split_ranges = json.loads(file.read())
    else:
        split_ranges = None


    try:
        alignment_path = inputs['Text Alignment JSON'][0]['resource_path']
    except KeyError:
        syls = None
    else:
        with open(alignment_path, 'r') as file:
            syls = json.loads(file.read())

    classifier_table, width_container = pct.fetch_table_from_csv(inputs['MEI Mapping CSV'][0]['resource_path'])
    width_mult = settings[u'Neume Component Spacing']
    mei_string = bm.process(jsomr, syls, classifier_table, width_mult, width_container, split_ranges)

    outfile_path = outputs['MEI'][0]['resource_path']
    with open(outfile_path, 'w') as file:
        file.write(mei_string)


    return True

if __name__ == "__main__":
    import re
    input_jsomr = "../debug/mei-encoding-test-hpf.json" # path to hpf output
    input_text = "../debug/mei-encoding-test-ta.json" # path to text alignment json
    input_csd = "../debug/mei-encoding-test-csd.json" # path to column splitting data
    input_mei_mapping = "../meimapping.csv" # path to mei mapping csv
    output_path = "../debug/result.mei" # path to output mei
    gt_output_path = "/code/Rodan/rodan/test/files/mei-encoding-test.mei" # path to ground truth mei
    inputs = {
        "JSOMR": [{"resource_path":input_jsomr}],
        "Text Alignment JSON": [{"resource_path":input_text}],
        "MEI Mapping CSV": [{"resource_path":input_mei_mapping}],
        "Column Splitting Data": [{"resource_path":input_csd}]
    }
    outputs = {
        "MEI": [{"resource_path":output_path}]
    }
    settings = {
        "Neume Component Spacing":0.5
    }

    run_my_task(inputs=inputs, outputs=outputs, settings=settings)

    # validate the output against the ground truth
    # Read the gt and predicted result
    with open(output_path, "r") as fp:
        predicted = [l.strip() for l in fp.readlines()]
    with open(gt_output_path, "r") as fp:
        gt = [l.strip() for l in fp.readlines()]

    pattern = re.compile(r"m-\w{8}-\w{4}-\w{4}-\w{4}-\w{12}")
    for i, (gt_line, pred_line) in enumerate(zip(gt, predicted)):
        # Replace ids
        gt_line = pattern.sub("_", gt_line)
        pred_line = pattern.sub("_", pred_line)
        # and compare if two meis are identical to each other
        if(gt_line != pred_line):
            print("failed at line {}".format(i))
        else:
            print("passed at line {}".format(i))
