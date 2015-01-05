import json
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import ImageDraw
from rodan.jobs.base import RodanAutomaticTask, RodanManualTask, ManualJobException
from rodan.jobs.gamera import argconvert
from gamera.toolkits.rodan_plugins.plugins.rdn_despeckle import rdn_despeckle
from django.template.loader import get_template

fn = rdn_despeckle.module.functions[0]

class ManualDespeckleTask(RodanManualTask):
    name = '{0}_manual'.format(str(fn))
    author = "Ling-Xiao Yang"
    description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = []
    enabled = True
    category = rdn_despeckle.module.category

    input_port_types = [{
        'name': 'image',
        'resource_types': map(argconvert.convert_pixel_to_mimetype, fn.self_type.pixel_types),
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'parameters',
        'resource_types': ['application/json'],
        'minimum': 1,
        'maximum': 1
    }]

    def get_my_interface(self, inputs, settings):
        t = get_template('gamera/interfaces/rdn_despeckle.html')
        c = {
            'image_url_large': inputs['image'][0]['large_thumb_url'],
            'image_url_small': inputs['image'][0]['small_thumb_url'],
        }
        return (t, c)

    def save_my_user_input(self, inputs, settings, outputs, userdata):
        parameters = {}
        try:
            parameters['cc_size'] = int(userdata.get('cc_size'))
        except ValueError:
            raise ManualJobException("Invalid cc_size")

        try:
            parameters['image_width'] = int(userdata.get('image_width'))
        except ValueError:
            raise ManualJobException("Invalid image width")

        with open(outputs['parameters'][0]['resource_path'], 'w') as g:
            json.dump(parameters, g)


class ApplyDespeckleTask(RodanAutomaticTask):
    name = '{0}_apply_despeckle'.format(str(fn))
    author = "Ling-Xiao Yang"
    description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = []
    enabled = True
    category = rdn_despeckle.module.category

    input_port_types = [{
        'name': 'image',
        'resource_types': map(argconvert.convert_pixel_to_mimetype, fn.self_type.pixel_types),
        'minimum': 1,
        'maximum': 1
    }, {
        'name': 'parameters',
        'resource_types': ['application/json'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'output',
        'resource_types': map(argconvert.convert_pixel_to_mimetype, fn.return_type.pixel_types),
        'minimum': 1,
        'maximum': 1
    }]

    def run_my_task(self, inputs, rodan_job_settings, outputs):
        task_image = load_image(inputs['image'][0]['resource_path'])
        with open(inputs['parameters'][0]['resource_path']) as f:
            parameters = json.load(f)
        result_image = task_image.rdn_despeckle(**parameters)
        result_image.save_PNG(outputs['output'][0]['resource_path'])
