import json
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import Image
from PIL import ImageDraw
from rodan.jobs.base import RodanAutomaticTask, RodanManualTask, ManualJobException
from rodan.jobs.gamera import argconvert
from django.template.loader import get_template


class ManualMaskTask(RodanManualTask):
    name = 'gamera.interactive_tasks.border_removal.poly_mask.manual'
    author = "Ling-Xiao Yang"
    description = "TODO"
    settings = {}
    enabled = True
    category = "Border Removal"

    input_port_types = [{
        'name': 'image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'polygon',
        'resource_types': ['application/json'],
        'minimum': 1,
        'maximum': 1
    }]

    def get_my_interface(self, inputs, settings):
        t = get_template('gamera/interfaces/poly_mask.html')
        # [TODO] don't let gamera run in Django thread. Try to find a more lightweight method.
        task_image = load_image(inputs['image'][0]['resource_path'])
        width = task_image.ncols
        c = {
            'image_url': inputs['image'][0]['large_thumb_url'],
            'image_width': task_image.ncols
        }
        return (t, c)

    def save_my_user_input(self, inputs, settings, outputs, userdata):
        if 'polygon_outer_points' not in userdata:
            raise ManualJobException("Bad data")
        # [TODO] validate userdata
        with open(outputs['polygon'][0]['resource_path'], 'w') as g:
            points = json.loads(userdata['polygon_outer_points'])
            json.dump(points, g)

class ApplyMaskTask(RodanAutomaticTask):
    name = 'gamera.interactive_tasks.border_removal.poly_mask.apply'
    author = "Deepanjan Roy"
    description = "TODO"
    settings = {}
    enabled = True
    category = "Border Removal"

    input_port_types = [{
        'name': 'image',
        'resource_types': ['image/onebit+png'],
        'minimum': 1,
        'maximum': 1
    }, {
        'name': 'polygon',
        'resource_types': ['application/json'],
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
        task_image = load_image(inputs['image'][0]['resource_path'])

        mask_img = Image.new('L', (task_image.ncols, task_image.nrows), color='white')
        mask_drawer = ImageDraw.Draw(mask_img)

        with open(inputs['polygon'][0]['resource_path']) as f:
            polygon_data = json.load(f)

        for polygon in polygon_data:
            flattened_poly = [j for i in polygon for j in i]
            mask_drawer.polygon(flattened_poly, outline='black', fill='black')
        del mask_drawer

        task_image_greyscale = task_image.to_greyscale()    # Because gamera masking doesn't work on one-bit images
        segment_mask = from_pil(mask_img).to_onebit()
        result_image_greyscale = task_image_greyscale.mask(segment_mask)
        result_image = result_image_greyscale.to_onebit()   # Get it back to one-bit

        result_image.save_PNG(outputs['output'][0]['resource_path'])
