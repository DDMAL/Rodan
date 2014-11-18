import json
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import Image
from PIL import ImageDraw
from rodan.jobs.base import RodanAutomaticTask


class PolyMaskTask(RodanAutomaticTask):
    name = 'gamera.custom.border_removal.poly_mask'
    author = "Deepanjan Roy"
    description = "TODO"

    settings = [{'visibility': False, 'default': 0, 'has_default': True, 'rng': (-1048576, 1048576), 'name': 'image_width', 'type': 'int'},
                {'visibility': False, 'default': None, 'has_default': True, 'name': 'polygon_outer_points', 'type': 'json'}]

    enabled = True
    category = "Border Removal"
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

    def run_my_task(self, inputs, rodan_job_settings, outputs):
        settings = argconvert.convert_to_gamera_settings(rodan_job_settings)
        task_image = load_image(inputs['input'][0]['resource_path'])

        mask_img = Image.new('L', (task_image.ncols, task_image.nrows), color='white')
        mask_drawer = ImageDraw.Draw(mask_img)

        try:
            polygon_data = json.loads(settings['polygon_outer_points'])
        except ValueError:
            # There's a problem in the JSON - it may be malformed, or empty
            polygon_data = []

        for polygon in polygon_data:
            flattened_poly = [j for i in polygon for j in i]
            mask_drawer.polygon(flattened_poly, outline='black', fill='black')
        del mask_drawer

        task_image_greyscale = task_image.to_greyscale()    # Because gamera masking doesn't work on one-bit images
        segment_mask = from_pil(mask_img).to_onebit()
        result_image_greyscale = task_image_greyscale.mask(segment_mask)
        result_image = result_image_greyscale.to_onebit()   # Get it back to one-bit

        result_image.save_image(outputs['output'][0]['resource_path'])
