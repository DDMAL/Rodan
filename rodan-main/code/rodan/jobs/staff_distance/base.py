from rodan.jobs.base import RodanTask
import cv2 as cv
import logging
import json
logger = logging.getLogger('rodan')

class StaffDistance(RodanTask):
    name = 'Staff Distance Finding'
    author = 'Zhanna Klimanova, Anthony Tan'
    description = 'Finds distance between staff lines. Returns distance and distance / 64.'
    enabled = True
    category = 'OMR - Layout analysis'
    interactive = False

    settings = {
        'title': 'Settings',
        'type': 'object',
        'job_queue': 'GPU',
    }

    input_port_types = [
        {'name': 'Input Image', 'minimum': 1, 'maximum': 1, 'resource_types': ['image/rgb+png']},
    ]

    output_port_types = [
        {
        'name': 'Resize Ratio',
        'resource_types': ['application/json'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
        }
    ]

    def run_my_task(self, inputs, settings, outputs):
        from .count_lines import preprocess_image, calculate_via_slices
        image_path = inputs['Input Image'][0]['resource_path']
        image = cv.imread(image_path,cv.IMREAD_UNCHANGED)
        processed = preprocess_image(image)
        distance = calculate_via_slices(processed)
        ratio = 64 / distance
        

        out_json_file = outputs['Resize Ratio'][0]['resource_path']

        out_json = {
            'distance': distance,
            'ratio': ratio
        }
        with open(out_json_file, 'w') as f:
            json.dump(out_json, f)


        return True