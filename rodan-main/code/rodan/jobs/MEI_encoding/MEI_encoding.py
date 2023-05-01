# -*- coding: utf-8 -*-
from rodan.jobs.base import RodanTask
from rodan.jobs.MEI_encoding import build_mei_file as bm
from rodan.jobs.MEI_encoding import parse_classifier_table as pct
import json

from celery.utils.log import get_task_logger


class MEI_encoding(RodanTask):
    name = 'MEI Encoding'
    author = 'Tim de Reuse'
    description = 'Builds an MEI file from pitchfinding information and transcript alignment results.'
    enabled = True
    category = "Encoding"
    interactive = False
    logger = get_task_logger(__name__)

    settings = {
        'title': 'Mei Encoding Settings',
        'type': 'object',
        'job_queue': 'Python3',
        'required': ['Neume Component Spacing'],
        'properties': {
            'Neume Component Spacing': {
                'type': 'number',
                'default': 0.5,
                'minimum': 0.0,
                'maximum': 10.0,
                'description': 'A multiplier controlling the spacing allowed between two neume components when grouping into neumes. 1.0 will use the median width of all glyphs on the page, 2.0 will use twice the median width, and so on. At 0, neume components will not be merged together, and each one will be treated as its own neume.',
            }
        }
    }

    input_port_types = [{
        'name': 'JSOMR',
        'resource_types': ['application/json'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }, {
        'name': 'Text Alignment JSON',
        'resource_types': ['application/json'],
        'minimum': 0,
        'maximum': 1,
        'is_list': False
    }, {
        'name': 'MEI Mapping CSV',
        'resource_types': ['text/csv'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }
    ]

    output_port_types = [{
        'name': 'MEI',
        'resource_types': ['application/mei+xml'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }]

    def run_my_task(self, inputs, settings, outputs):
        self.logger.info(settings)

        jsomr_path = inputs['JSOMR'][0]['resource_path']
        self.logger.info('loading jsomr...')
        with open(jsomr_path, 'r') as file:
            jsomr = json.loads(file.read())

        try:
            alignment_path = inputs['Text Alignment JSON'][0]['resource_path']
        except KeyError:
            self.logger.warning('no text alignment given! using dummy syllables...')
            syls = None
        else:
            self.logger.info('loading text alignment results..')
            with open(alignment_path, 'r') as file:
                syls = json.loads(file.read())

        self.logger.info('fetching classifier...')
        classifier_table, width_container = pct.fetch_table_from_csv(inputs['MEI Mapping CSV'][0]['resource_path'])
        width_mult = settings[u'Neume Component Spacing']
        mei_string = bm.process(jsomr, syls, classifier_table, width_mult, width_container)

        self.logger.info('writing to file...')
        outfile_path = outputs['MEI'][0]['resource_path']
        with open(outfile_path, 'w') as file:
            file.write(mei_string)

        return True

    def test_my_task(self, testcase):
        import re
        input_jsomr = "/code/Rodan/rodan/test/files/238r-heuristic_pitch_finding.json"
        input_text = "/code/Rodan/rodan/test/files/238r-text-alignment.json"
        input_mei_mapping = "/code/Rodan/rodan/test/files/238r-mei-mapping.csv"
        output_path = testcase.new_available_path()
        gt_output_path = "/code/Rodan/rodan/test/files/238r-mei.mei"
        inputs = {
            "JSOMR": [{"resource_path":input_jsomr}],
            "Text Alignment JSON": [{"resource_path":input_text}],
            "MEI Mapping CSV": [{"resource_path":input_mei_mapping}]
        }
        outputs = {
            "MEI": [{"resource_path":output_path}]
        }
        settings = {
            "Neume Component Spacing":0.5
        }

        self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

        # Read the gt and predicted result
        with open(output_path, "r") as fp:
            predicted = [l.strip() for l in fp.readlines()]
        with open(gt_output_path, "r") as fp:
            gt = [l.strip() for l in fp.readlines()]

        # The number lines should be identical
        testcase.assertEqual(len(gt), len(predicted))

        # also each line should be identical to its counterpart
        # Since mei encoding creates unique ids, we use regex to replace each id with an underscore
        pattern = re.compile(r"m-\w{8}-\w{4}-\w{4}-\w{4}-\w{12}")
        for i, (gt_line, pred_line) in enumerate(zip(gt, predicted)):
            # Replace ids
            gt_line = pattern.sub("_", gt_line)
            pred_line = pattern.sub("_", pred_line)
            # and compare if two meis are identical to each other
            testcase.assertEqual(gt_line, pred_line, "Line {}".format(i))

        del predicted, gt