from rodan.jobs.base import RodanTask
from .column_split import *
import cv2 as cv
import os
import json
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
        {'name': 'Music Notes Layer', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Text Layer', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
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
        {'name': 'Music Notes Layer', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Text Layer', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'All Layers', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 5', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 6', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 7', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 8', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 9', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {'name': 'Layer 10', 'minimum': 0, 'maximum': 1, 'resource_types': ['image/rgba+png']},
        {
        'name': 'Column Splitting Data',
        'resource_types': ['application/json'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
        }
    )

    def run_my_task(self, inputs, settings, outputs):
        logger.info("Running Column Splitting")
        num_columns = settings['Number of columns']

        staff_layer = inputs['Staff Layer'][0]['resource_path']
        text_layer = inputs['Text Layer'][0]['resource_path']
        neume_layer = inputs['Music Notes Layer'][0]['resource_path']

        staff = cv.imread(staff_layer,cv.IMREAD_UNCHANGED)
        text = cv.imread(text_layer,cv.IMREAD_UNCHANGED)
        neume = cv.imread(neume_layer,cv.IMREAD_UNCHANGED)

        gray_text = convert_to_grayscale(text) == False
        gray_staff = convert_to_grayscale(staff) == False
        gray_neume = convert_to_grayscale(neume) == False
        
        logger.info("Merging the three layers")
        merged = get_merged_layers([gray_text,gray_staff,gray_neume])
        logger.info("Getting split locations")
        split_locations = get_split_locations(merged,num_columns)
        logger.info("Getting split ranges")
        ranges = get_split_ranges(merged,split_locations)
        logger.info("Getting stacked images")
        
        stacked_text = get_stacked_image(text,ranges)
        stacked_staff = get_stacked_image(staff,ranges)
        stacked_neume = get_stacked_image(neume,ranges)


        outfile_staff = outputs['Staff Layer'][0]['resource_path']
        cv.imwrite(outfile_staff+".png",stacked_staff)
        os.rename(outfile_staff+".png", outfile_staff)

        outfile_text = outputs['Text Layer'][0]['resource_path']
        cv.imwrite(outfile_text+".png",stacked_text)
        os.rename(outfile_text+".png", outfile_text)

        outfile_neume = outputs['Music Notes Layer'][0]['resource_path']
        cv.imwrite(outfile_neume+".png",stacked_neume)
        os.rename(outfile_neume+".png", outfile_neume)

        layers = [staff,text,neume]
        
        for key in inputs:
            if key != 'Staff Layer' and key != 'Text Layer' and key != 'Music Notes Layer' and key != 'All Layers':
                layer = inputs[key][0]['resource_path']
                img = cv.imread(layer,cv.IMREAD_UNCHANGED)
                layer_stacked = get_stacked_image(img,ranges)
                layers.append(img)
                if key in outputs:
                    outfile = outputs[key][0]['resource_path']
                    cv.imwrite(outfile+".png",layer_stacked)
                    os.rename(outfile+".png", outfile)
        
        if 'All Layers' in outputs:
            outfile_all = outputs['All Layers'][0]['resource_path']
            final = get_stacked_image(layers[0],ranges)
            for layer in layers[1:]:
                final = final + get_stacked_image(layer,ranges)
            cv.imwrite(outfile_all+".png",final)
            os.rename(outfile_all+".png", outfile_all)

        out_json_file = outputs['Column Splitting Data'][0]['resource_path']

        out_json = {
            'width': merged.shape[1],
            'height': merged.shape[0],
            'split_ranges': ranges,
        }
        with open(out_json_file, 'w') as f:
            json.dump(out_json, f)

        return True