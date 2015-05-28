import json
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import Image
from PIL import ImageDraw
from rodan.jobs.base import RodanTask
from rodan.jobs.gamera import argconvert
from rodan.jobs.gamera.base import ensure_pixel_type

class PolyMask(RodanTask):
    name = 'gamera.border_removal.poly_mask'
    author = "Ling-Xiao Yang"
    description = "Interactive border removal."
    settings = {}
    enabled = True
    category = "Border Removal"
    interactive = True

    input_port_types = [{
        'name': 'input',
        'resource_types': ['image/onebit+png', 'image/greyscale+png', 'image/grey16+png', 'image/rgb+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'output',
        'resource_types': ['image/onebit+png', 'image/greyscale+png', 'image/grey16+png', 'image/rgb+png'],
        'minimum': 1,
        'maximum': 1
    }]

    def run_my_task(self, inputs, settings, outputs):
        if '@polygon_outer_points' not in settings:
            task_image = load_image(inputs['input'][0]['resource_path'])
            settings_update = {'@image_width': task_image.ncols}
            return self.WAITING_FOR_INPUT(settings_update)
        else:
            task_image = load_image(inputs['input'][0]['resource_path'])

            mask_img = Image.new('L', (task_image.ncols, task_image.nrows), color='white')
            mask_drawer = ImageDraw.Draw(mask_img)

            polygon_outer_points = settings['@polygon_outer_points']
            for polygon in polygon_outer_points:
                flattened_poly = [j for i in polygon for j in i]
                mask_drawer.polygon(flattened_poly, outline='black', fill='black')
            del mask_drawer

            task_image_rgb = task_image.to_rgb()    # Because gamera masking doesn't work on onebit or grey16 images.
            segment_mask = from_pil(mask_img).to_onebit()
            result_image_rgb = task_image_rgb.mask(segment_mask)
            result_image = ensure_pixel_type(result_image_rgb, outputs['output'][0]['resource_type'])

            result_image.save_PNG(outputs['output'][0]['resource_path'])

    def get_my_interface(self, inputs, settings):
        t = 'interfaces/poly_mask.html'
        c = {
            'image_url': inputs['input'][0]['large_thumb_url'],
            'image_width': settings['@image_width']
        }
        return (t, c)

    def validate_my_user_input(self, inputs, settings, user_input):
        if 'polygon_outer_points' not in user_input:
            raise self.ManualPhaseException("Bad data")
        # [TODO] validate userdata
        return {'@polygon_outer_points': user_input['polygon_outer_points']}
