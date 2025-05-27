from rodan.jobs.base import RodanTask
try:
    from gamera.core import load_image, init_gamera
    from gamera import gamera_xml
    from .StaffFinding import StaffFinder
    from .PitchFinding import PitchFinder
    init_gamera()
except ImportError:
    pass

import sys
import json
import json.encoder




class MiyaoStaffinding(RodanTask):
    name = 'Miyao Staff Finding'
    author = 'Noah Baxter'
    description = 'Finds the location of staves in an image and returns them as a JSOMR file.'
    enabled = True
    category = 'aOMR'
    interactive = False

    settings = {
        'title': 'Settings',
        'type': 'object',
        'job_queue': 'Python3',
        'required': ['Number of lines', 'Interpolation'],
        'properties': {
            'Number of lines': {
                'type': 'integer',
                'default': 4,
                'minimum': 0,
                'maximum': 8,
                'description': 'Number of lines within each staff. When zero, the number is automatically detected.'
            },
            'Interpolation': {
                'type': 'boolean',
                'default': True,
                'description': 'Interpolate found line points so all lines have the same number of points. This MUST be True for pitch finding to succeed.'
            }
        }
    }

    input_port_types = [{
        'name': 'Image containing staves (RGB, greyscale, or onebit)',
        'resource_types': ['image/rgb+png', 'image/onebit+png', 'image/greyscale+png'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }]

    output_port_types = [{
        'name': 'JSOMR',
        'resource_types': ['application/json'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }]

    def run_my_task(self, inputs, settings, outputs):

        # Inputs
        image = load_image(inputs['Image containing staves (RGB, greyscale, or onebit)'][0]['resource_path'])
        kwargs = {
            'lines_per_staff': settings['Number of lines'],
            'staff_finder': 0,          # 0 for miyao
            'binarization': 1,
            'interpolation': settings['Interpolation'],
        }

        sf = StaffFinder(**kwargs)

        page = sf.get_page_properties(image)
        staves = sf.get_staves(image)

        jsomr = {
            'page': page,
            'staves': staves,
        }

        # Outputs
        outfile_path = outputs['JSOMR'][0]['resource_path']
        with open(outfile_path, "w") as outfile:
            outfile.write(json.dumps(jsomr))

        return True

    def test_my_task(self, testcase):
        import cv2
        import numpy as np
        input_dilate_png_path = "/code/Rodan/rodan/test/files/ms73-068_dilate_output.png"
        output_path = testcase.new_available_path()
        gt_output_path = "/code/Rodan/rodan/test/files/ms73-068-miyao-staff-finding.json"
        inputs = {
            "Image containing staves (RGB, greyscale, or onebit)": [{"resource_path":input_dilate_png_path}]
        }
        outputs = {
            "JSOMR": [{"resource_path":output_path}]
        }
        settings = {'Number of lines': 4, 'Interpolation': True}

        self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

        # Read the gt and predicted result
        with open(output_path, "r") as fp:
            predicted = [l.strip() for l in fp.readlines()]
        with open(gt_output_path, "r") as fp:
            gt = [l.strip() for l in fp.readlines()]

        # The number lines should be identical
        testcase.assertEqual(len(gt), len(predicted))
        # also each line should be identical to its counterpart
        for i, (gt_line, pred_line) in enumerate(zip(gt, predicted)):
            testcase.assertEqual(gt_line, pred_line, "Line {}".format(i))


class HeuristicPitchFinding(RodanTask):
    name = 'Heuristic Pitch Finding'
    author = 'Noah Baxter'
    description = 'Calculates pitch values for Classified Connected Componenets from a JSOMR containing staves, and returns the results as a JSOMR file'
    settings = {
        'title': 'aOMR settings',
        'type': 'object',
        'job_queue': 'Python3',

        'required': ['Discard Size'],
        'properties': {
            'Discard Size': {
                'type': 'integer',
                'default': 12,
                'minimum': 5,
                'maximum': 25,
                'description': '',
            },
        }
    }
    enabled = True
    category = 'aOMR'
    interactive = False
    input_port_types = [{
        'name': 'JSOMR of staves and page properties',
        'resource_types': ['application/json'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    },
        {
        'name': 'GameraXML - Classified Connected Components',
        'resource_types': ['application/gamera+xml'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }]
    output_port_types = [{
        'name': 'JSOMR of glyphs, staves, and page properties',
        'resource_types': ['application/json'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }]

    def run_my_task(self, inputs, settings, outputs):

        # Inputs
        infile_path = inputs['JSOMR of staves and page properties'][0]['resource_path']
        with open(infile_path, 'r') as infile:
            jsomr_string = infile.read()

        jsomr = json.loads(jsomr_string)
        glyphs = gamera_xml.glyphs_from_xml(inputs['GameraXML - Classified Connected Components'][0]['resource_path'])

        kwargs = {
            'discard_size': settings['Discard Size'],
        }

        pf = PitchFinder(**kwargs)

        page = jsomr['page']
        staves = jsomr['staves']
        pitches = pf.get_pitches(glyphs, staves)

        # Outputs
        jsomr = {
            'page': page,
            'staves': staves,
            'glyphs': pitches,
        }
        #jsomr = json.decoder(jsomr)


        def rec_serialize(byte2str):
 
            """
            A recursive function that iterates over a JSON object and changes all the bytes values to string
            """
            # dealing with dictionaries and lists and other stuff as three categories
            if type(byte2str) == list:
                # recursively for all elements 
                for index in range(len(byte2str)):
                    element = byte2str[index]
                    byte2str[index] = rec_serialize(element)

            elif type(byte2str) == dict:
                for key in byte2str:
                    value = byte2str[key]
                    byte2str[key] = rec_serialize(value)
            elif type(byte2str) == bytes:
                # the element must be decoded
                return byte2str.decode("UTF-8")

            return byte2str

        outfile_path = outputs['JSOMR of glyphs, staves, and page properties'][0]['resource_path']
        
        with open(outfile_path, "w") as outfile:
            serialized = rec_serialize(jsomr)
            r = json.dumps(serialized)
            outfile.write(r)

        return True

    def test_my_task(self, testcase):
        import cv2
        import numpy as np
        input_nic_path = "/code/Rodan/rodan/test/files/238r-nic.xml"
        input_staff_finding_path = "/code/Rodan/rodan/test/files/238r-miyao-staff-finding.json"
        output_path = testcase.new_available_path()
        gt_output_path = "/code/Rodan/rodan/test/files/238r-heuristic_pitch_finding.json"

        inputs = {
            "JSOMR of staves and page properties": [{"resource_path":input_staff_finding_path}],
            "GameraXML - Classified Connected Components": [{"resource_path":input_nic_path}]
        }
        outputs = {
            "JSOMR of glyphs, staves, and page properties": [{"resource_path":output_path}]
        }
        settings = {'Discard Size': 12}

        self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

        # Read the gt and predicted result
        with open(output_path, "r") as fp:
            predicted = [l.strip() for l in fp.readlines()]
        with open(gt_output_path, "r") as fp:
            gt = [l.strip() for l in fp.readlines()]

        # The number lines should be identical
        testcase.assertEqual(len(gt), len(predicted))
        # also each line should be identical to its counterpart
        for i, (gt_line, pred_line) in enumerate(zip(gt, predicted)):
            testcase.assertEqual(gt_line, pred_line, "Line {}".format(i))
