import json
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import ImageDraw
from rodan.jobs.base import RodanAutomaticTask, RodanManualTask, ManualJobException
from rodan.jobs.gamera import argconvert
from gamera.toolkits.rodan_plugins.plugins.rdn_crop import rdn_crop

fn = rdn_crop.module.functions[0]

class ManualCropTask(RodanManualTask):
    name = '{0}_manual'.format(str(fn))
    author = "Ling-Xiao Yang"
    description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = []
    enabled = True
    category = rdn_crop.module.category

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
        t = get_template('gamera/interfaces/rdn_crop.html')
        c = {
            'image_url': inputs['image'][0]['large_thumb_url'],
        }
        return (t, c)

    def save_my_user_input(self, inputs, settings, outputs, userdata):
        parameters = {}
        try:
            parameters['ulx'] = float(userdata.get('ulx'))
        except ValueError:
            raise ManualJobException("Invalid ulx")

        try:
            parameters['uly'] = float(userdata.get('uly'))
        except ValueError:
            raise ManualJobException("Invalid uly")

        try:
            parameters['lrx'] = float(userdata.get('lrx'))
        except ValueError:
            raise ManualJobException("Invalid lrx")

        try:
            parameters['lry'] = float(userdata.get('lry'))
        except ValueError:
            raise ManualJobException("Invalid lry")

        try:
            parameters['imw'] = float(userdata.get('imw'))
        except ValueError:
            raise ManualJobException("Invalid imw")

        with open(outputs['parameters'][0]['resource_path'], 'w') as g:
            json.dump(parameters, g)


class ApplyCropTask(RodanAutomaticTask):
    name = '{0}_apply_crop'.format(str(fn))
    author = "Ling-Xiao Yang"
    description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = []
    enabled = True
    category = rdn_crop.module.category

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
        result_image = task_image.rdn_crop(**parameters)
        result_image.save_image(outputs['output'][0]['resource_path'])
