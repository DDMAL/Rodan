# Copyright (C) 2020 Juliette Regimbal
# SPDX-License-Identifier: GPL-3.0-or-later


import pymei

from celery.utils.log import get_task_logger
from rodan.jobs.base import RodanTask


def recurse_scale(factor, element):
    """Scale down coordinated atts of element and its descendants"""
    if element.hasAttribute('ulx'):
        ulx = element.getAttribute('ulx')
        ulx.setValue(str(int(int(ulx.getValue()) * factor)))
    if element.hasAttribute('uly'):
        uly = element.getAttribute('uly')
        uly.setValue(str(int(int(uly.getValue()) * factor)))
    if element.hasAttribute('lrx'):
        lrx = element.getAttribute('lrx')
        lrx.setValue(str(int(int(lrx.getValue()) * factor)))
    if element.hasAttribute('lry'):
        lry = element.getAttribute('lry')
        lry.setValue(str(int(int(lry.getValue()) * factor)))

    for child in element.getChildren():
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
        'job_queue': 'Python2',
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

        doc = pymei.documentFromFile(input_path)
        mei = doc.getMeiDocument()
        facsimiles = mei.getElementsByName('facsimile')
        if len(facsimiles) > 0:
            pass
        else:
            self.logger.warn("No facsimiles in this file!")

        recurse_scale(factor, facsimiles[0])
        result = pymei.documentToFile(mei, output_path)
        self.logger.info("Result: {}".format(result))
