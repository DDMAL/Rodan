from rodan.jobs.base import RodanTask

from gamera.core import load_image, init_gamera
from gamera import gamera_xml

from .StaffFinding import StaffFinder
from .PitchFinding import PitchFinder

import sys
import json
import json.encoder

init_gamera()


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

        outfile_path = outputs['JSOMR of glyphs, staves, and page properties'][0]['resource_path']
        
        with open(outfile_path, "w") as outfile:
            r = json.dumps(jsomr)
            outfile.write(r)

        return True
