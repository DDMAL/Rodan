from rodan.jobs.base import RodanTask
from .column_split import get_split_locations,get_split_ranges,get_stacked_image
import cv2 as cv
import os
import logging
logger = logging.getLogger('rodan')

class ColumnSplit(RodanTask):
    name = 'Column Splitting'
    author = 'Anthony Tan'
    description = 'Finds the locations of the columns of a folio based on the staff layers then stacks them into a single image.'
    enabled = True
    category = 'OMR - Layout analysis'
    interactive = False

    settings = {
        'title': 'Settings',
        'type': 'object',
        'job_queue': 'Python3',
        'required': ['Number of columns'],
        'properties': {
            'Number of columns': {
                'type': 'integer',
                'default': 2,
                'minimum': 2,
                'maximum': 10,
                'description': 'Number of columns in the folio. Must be at least 2. If there is only one, don\'t use this job.'
            }
        }
    }

    input_port_types = (
        {'name': 'Staff Layer', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Background Layer', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Music Notes Layer', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Text Layer', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 4', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 5', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 6', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 7', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 8', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 9', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 10', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
    )

    output_port_types = (
        {'name': 'Staff Layer', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Background Layer', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Music Notes Layer', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Text Layer', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 4', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 5', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 6', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 7', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 8', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 9', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 10', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
    )

    def run_my_task(self, inputs, settings, outputs):
        logger.info("Running Column Splitting")
        splits = settings['Number of columns']
        staff_layer = inputs['Staff Layer'][0]['resource_path']
        img = cv.imread(staff_layer,cv.IMREAD_UNCHANGED)
        logger.info("Getting split locations")
        split_locations = get_split_locations(img,splits)
        logger.info("Getting split ranges")
        ranges = get_split_ranges(img,split_locations)
        logger.info("Getting stacked images")
        staff_stacked = get_stacked_image(img,ranges)
        outfile = outputs['Staff Layer'][0]['resource_path']
        cv.imwrite(outfile+".png",staff_stacked)
        os.rename(outfile+".png", outfile)

        for key in inputs:
            if key != 'Staff Layer':
                layer = inputs[key][0]['resource_path']
                img = cv.imread(layer,cv.IMREAD_UNCHANGED)
                logger.info("Getting stacked images")
                layer_stacked = get_stacked_image(img,ranges)
                outfile = outputs[key][0]['resource_path']
                cv.imwrite(outfile+".png",layer_stacked)
                os.rename(outfile+".png", outfile)
        return True