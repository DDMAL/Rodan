import json
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import Image
from PIL import ImageDraw
from gamera.toolkits.musicstaves.stafffinder_miyao import StaffFinder_miyao
from rodan.jobs.gamera.custom.segmentation.poly_lists import fix_poly_point_list, create_polygon_outer_points_json_dict
from rodan.jobs.base import RodanTask
from rodan.jobs.gamera import argconvert
from django.template.loader import get_template


class Segmentation(RodanTask):
    name = 'gamera.segmentation.segmentation'
    author = "Deepanjan Roy"
    description = "Finds the staves using Miyao Staff Finder and masks out everything else."
    settings = {
        'type': 'object',
        'required': ['num_lines', 'scanlines', 'blackness', 'tolerance'],
        'properties': {
            'num_lines': {
                'type': 'integer',
                'default': 0,
                'minimum': -1048576,
                'maximum': 1048576
            },
            'scanlines': {
                'type': 'integer',
                'default': 5,
                'minimum': -1048576,
                'maximum': 1048576
            },
            'blackness': {
                'type': 'number',
                'default': 0.8,
                'minimum': -1048576,
                'maximum': 1048576
            },
            'tolerance': {
                'type': 'integer',
                'default': -1,
                'minimum': -1048576,
                'maximum': 1048576
            }
        }
    }
    enabled = True
    category = "Segmentation"
    interactive = True

    input_port_types = [{
        'name': 'input',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'output',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]

    def run_my_task(self, inputs, settings, outputs):
        if '@polygon_outer_points' not in settings:
            task_image = load_image(inputs['input'][0]['resource_path'])

            ranked_page = task_image.rank(9, 9, 0)
            staff_finder = StaffFinder_miyao(ranked_page, 0, 0)
            staff_finder.find_staves(**settings)

            poly_list = staff_finder.get_polygon()
            poly_list = fix_poly_point_list(poly_list, staff_finder.staffspace_height)
            poly_json_list = create_polygon_outer_points_json_dict(poly_list)

            settings_update = {
                '@image_width': task_image.ncols,
                '@polygon_outer_points': poly_json_list
            }
            return self.WAITING_FOR_INPUT(settings_update)
        else:
            task_image = load_image(inputs['input'][0]['resource_path'])
            mask_img = Image.new('L', (task_image.ncols, task_image.nrows), color='white')
            mask_drawer = ImageDraw.Draw(mask_img)

            for polygon in settings['@polygon_outer_points']:
                flattened_poly = [j for i in polygon for j in i]
                mask_drawer.polygon(flattened_poly, outline='black', fill='black')
            del mask_drawer

            task_image_greyscale = task_image.to_greyscale()    # Because gamera masking doesn't work on one-bit images
            segment_mask = from_pil(mask_img).to_onebit()
            result_image_greyscale = task_image_greyscale.mask(segment_mask)
            result_image = result_image_greyscale.to_onebit()   # Get it back to one-bit

            result_image.save_PNG(outputs['output'][0]['resource_path'])

    def get_my_interface(self, inputs, settings):
        t = get_template('gamera/interfaces/segmentation.html')
        c = {
            'image_url': inputs['input'][0]['large_thumb_url'],
            'polygon_outer_points': settings['@polygon_outer_points'],
            'image_width': settings['@image_width']
        }
        return (t, c)

    def validate_my_user_input(self, inputs, settings, user_input):
        points = json.loads(user_input.get('polygon_outer_points'))
        # [TODO] validate input
        return {'@polygon_outer_points': points}
