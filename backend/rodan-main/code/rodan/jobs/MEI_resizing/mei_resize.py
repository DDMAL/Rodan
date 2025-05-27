# Copyright (C) 2020 Juliette Regimbal
# SPDX-License-Identifier: GPL-3.0-or-later


import lxml.etree as ET  #must use lxml not elementTree due to bug in python 3.7 (resolved in 3.8)
from celery.utils.log import get_task_logger
from rodan.jobs.base import RodanTask



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
    if (element.get('lry') is not None):
        lry = element.get('lry')
        element.set('lry', str(int(int(lry) * factor)))

    children = list(element)
    for child in children:
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

        recurse_scale(factor, facsHead[0])  #to input the surface

        tree = ET.ElementTree(meiDoc.getroot())
        
        self.logger.info('writing to file...')
        tree.write(output_path, xml_declaration=True, encoding='UTF-8')

    def test_my_task(self, testcase):
        def parse_recursive(factor, element, ret_list) -> list:
            """Scale down coordinated atts of element and its descendants"""
            for key in ["ulx", "uly", "lrx", "lry"]:
                if (element.get(key) is not None):
                    position = element.get(key)
                    ret_list.append(int(position))

            children = list(element)
            for child in children:
                parse_recursive(factor, child, ret_list)

            return ret_list

        import os
        input_path = "/code/Rodan/rodan/test/files/CF-005.mei"
        scale = 0.7
        inputs = {
            "MEI": [
                {"resource_path":input_path}
            ]
        }
        outputs = {
            "MEI": [
                {"resource_path":testcase.new_available_path()}
            ]
        }
        settings = {
            "Scale Factor":scale
        }
        self.run_my_task(inputs=inputs, outputs=outputs, settings=settings)

        # Read and parse the input MEI
        input_mei = ET.parse(input_path)
        input_head = input_mei.getroot()[1][0][0]
        input_positions = parse_recursive (0.5, input_head, [])
        # Read and parse the output MEI
        output_mei = ET.parse(outputs["MEI"][0]["resource_path"])
        output_head = output_mei.getroot()[1][0][0]
        output_positions = parse_recursive (0.5, output_head, [])

        # MEI_scale does not change the number of elements. Two files should have the same length.
        testcase.assertEqual(len(input_positions), len(output_positions))

        # Go through each element. The position of the output element should be equal to 
        # the factor * the position of the input element.
        for input_pos, output_pos in zip(input_positions, output_positions):
            testcase.assertEqual(int(input_pos*scale), output_pos)



