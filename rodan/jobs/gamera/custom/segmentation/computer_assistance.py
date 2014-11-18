import json
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import Image
from PIL import ImageDraw
from gamera.toolkits.musicstaves.stafffinder_miyao import StaffFinder_miyao
from rodan.jobs.gamera.custom.segmentation.poly_lists import fix_poly_point_list, create_polygon_outer_points_json_dict
from rodan.jobs.base import RodanAutomaticTask


class ComputerAssistanceTask(RodanAutomaticTask):
    name = 'gamera.custom.segmentation.computer_assistance'
    author = "Deepanjan Roy"
    description = "Finds the staves using Miyao Staff Finder and masks out everything else."
    settings = [
        {'default': 0, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'num lines', 'type': 'int'},
        {'default': 5, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'scanlines', 'type': 'int'},
        {'default': 0.8, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'blackness', 'type': 'real'},
        {'default': -1, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'tolerance', 'type': 'int'},
    ]
    enabled = True
    category = "Segmentation"

    input_port_types = [{
        'name': 'input',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'output',
        'resource_types': ['application/vnd.rodan.interactive.directive+json'],
        'minimum': 1,
        'maximum': 1
    }]

    def run_my_task(self, inputs, rodan_job_settings, outputs):
        settings = argconvert.convert_to_gamera_settings(rodan_job_settings)
        task_image = load_image(inputs['input'][0]['resource_path'])

        ranked_page = task_image.rank(9, 9, 0)
        staff_finder = StaffFinder_miyao(ranked_page, 0, 0)
        staff_finder.find_staves(**settings)

        poly_list = staff_finder.get_polygon()
        poly_list = fix_poly_point_list(poly_list, staff_finder.staffspace_height)
        poly_json_list = create_polygon_outer_points_json_dict(poly_list)

        with open(outputs['output'][0]['resource_path'], 'w') as f:
            json.dump({
                'acceptable_interfaces': [
                    {
                        'name': 'segmentation',
                        'kwargs': {'image_width': task_image.ncols, 'polygon_outer_points': poly_json_list}
                    }
                ],
                'result': {'polygon_outer_points': poly_json_list}
             }, f)
