from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import ImageDraw
from rodan.jobs.base import RodanAutomaticTask, RodanManualTask, ManualJobException
from rodan.jobs.gamera import argconvert
from gamera.toolkits.rodan_plugins.plugins.rdn_rotate import rdn_rotate
from django.template.loader import get_template

fn = rdn_rotate.module.functions[0]

class ManualRotateTask(RodanManualTask):
    name = '{0}_manual'.format(str(fn))
    author = "Ling-Xiao Yang"
    description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = []
    enabled = True
    category = rdn_rotate.module.category

    input_port_types = [{
        'name': 'image',
        'resource_types': map(argconvert.convert_pixel_to_mimetype, fn.self_type.pixel_types),
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'angle',
        'resource_types': ['text/plain'],
        'minimum': 1,
        'maximum': 1
    }]

    def get_my_interface(self, inputs, settings):
        t = get_template('gamera/interfaces/rdn_rotate.html')
        c = {
            'image_url': inputs['image'][0]['large_thumb_url'],
        }
        return (t, c)

    def save_my_user_input(self, inputs, settings, outputs, userdata):
        if 'angle' not in userdata:
            raise ManualJobException("Bad data")
        angle = userdata['angle']
        try:
            float(angle)
        except ValueError:
            raise ManualJobException("Invalid angle")

        with open(outputs['angle'][0]['resource_path'], 'w') as g:
            g.write(angle)


class ApplyRotateTask(RodanAutomaticTask):
    name = '{0}_apply_rotate'.format(str(fn))
    author = "Ling-Xiao Yang"
    description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = []
    enabled = True
    category = rdn_rotate.module.category

    input_port_types = [{
        'name': 'image',
        'resource_types': map(argconvert.convert_pixel_to_mimetype, fn.self_type.pixel_types),
        'minimum': 1,
        'maximum': 1
    }, {
        'name': 'angle',
        'resource_types': ['text/plain'],
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
        with open(inputs['angle'][0]['resource_path']) as f:
            angle = float(f.read())
        result_image = task_image.rdn_rotate(angle)
        result_image.save_PNG(outputs['output'][0]['resource_path'])
