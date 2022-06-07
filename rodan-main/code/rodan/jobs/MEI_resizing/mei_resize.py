# Copyright (C) 2020 Juliette Regimbal
# SPDX-License-Identifier: GPL-3.0-or-later


import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring #more concise?

from celery.utils.log import get_task_logger
from rodan.jobs.base import RodanTask

#hasAttribute is the none thing 
#getAttribute is 
#setValue is 
#getValue is 

def recurse_scale(factor, element):
    """Scale down coordinated atts of element and its descendants"""
    if (element.get('ulx') is not None):
        ulx = element.get('ulx')
        element.set('ulx', str(int(int(ulx) * factor)))
    if (element.get('uly') is not None):
        uly = element.get('uly')
        element.set('uly', str(int(int(uly) * factor)))
    if (element.get('lrx') is not None):
        lrx = element.get('lrx')
        element.set('lrx', str(int(int(lrx) * factor)))
    if element.hasAttribute('lry'):
        lry = element.get('lry')
        element.set('lry', str(int(int(lry) * factor)))


    children = list(element)
    for child in range(len(children)):
        recurse_scale(factor, child)


class MEI_Resize(RodanTask):
    name = 'MEI Resizing'
    author = 'Juliette Regimbal'
    description = 'Scale the facsimile of an MEI file'
    enabled = True
    category = 'Encoding'
    interactive = False
    logger = get_task_logger(__name__)

    settings = {
        'job_queue': 'Python3',
        'type': 'object',
        'title': 'Settings',
        'properties': {
            'Scale Factor': {
                'type': 'number',
                'minimum': 0,
                'default': 1,
                'exclusiveMinimum': True,
                'description': 'Only used when scale input port is unused.'
            }
        }
    }

    input_port_types = [
        {
            'name': 'MEI',
            'minimum': 1,
            'maximum': 1,
            'resource_types': ['application/mei+xml']
        },
        {
            'name': 'Scale Value',
            'minimum': 0,
            'maximum': 1,
            'resource_types': ['text/plain']
        }
    ]

    output_port_types = [
        {
            'name': 'MEI',
            'minimum': 1,
            'maximum': 1,
            'resource_types': ['application/mei+xml']
        }
    ]

    def run_my_task(self, inputs, settings, outputs):
        self.logger.info(settings)

        if "Scale Value" in inputs:
            scale_path = inputs['Scale Value'][0]['resource_path']
            with open(scale_path, 'r') as f:
                factor = float(f.read())
        else:
            factor = settings['Scale Factor']

        self.logger.info("Attempting to scale by {}%...".format(factor * 100))

        input_path = inputs['MEI'][0]['resource_path']
        output_path = outputs['MEI'][0]['resource_path']

        meiDoc = ET.parse(input_path)
        mei = meiDoc.getroot()
        musicHead = mei[1]
        facsHead = musicHead[0]

        if len(facsHead) > 0:
            pass
        else:
            self.logger.warn("No facsimiles in this file!")

        recurse_scale(factor, facsHead[0])

        tree = ET.ElementTree(meiDoc.getroot())
        result = ET.tostring(tree.getroot(),encoding='utf8').decode('utf8')

        with open(output_path, 'w') as file:
            result = file.write(result)

        self.logger.info("Result: {}".format(result))
