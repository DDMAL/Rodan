import json, jsonschema
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import ImageDraw
from rodan.jobs.base import RodanAutomaticTask, RodanManualTask, ManualJobException
from rodan.jobs.gamera import argconvert
from rodan.jobs.gamera.base import ensure_pixel_type
from gamera.toolkits.rodan_plugins.plugins.rdn_despeckle import rdn_despeckle
from django.template.loader import get_template

fn = rdn_despeckle.module.functions[0]
i_type = argconvert.convert_input_type(fn.self_type)
o_type = argconvert.convert_output_type(fn.return_type)

class ManualDespeckleTask(RodanManualTask):
    name = '{0}_manual'.format(str(fn))
    author = "Ling-Xiao Yang"
    description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = {}
    enabled = True
    category = rdn_despeckle.module.category

    input_port_types = [{
        'name': 'image',
        'resource_types': i_type['resource_types'],
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

    validator = jsonschema.Draft4Validator({
        "type": "object",
        "required": ["cc_size", "image_width"],
        "properties": {
            "cc_size": {
                "description": "pixel size of connected components",
                "type": "integer",
                "minimum": 0   # inclusive
            },
            "image_width": {
                "description": "thumbnail image width",
                "type": "integer",
                "minimum": 0   # inclusive
            }
        }
    })
    def save_my_user_input(self, inputs, settings, outputs, userdata):
        try:
            self.validator.validate(userdata)
        except jsonschema.exceptions.ValidationError as e:
            raise ManualJobException(e.message)

        parameters = {
            'cc_size': userdata['cc_size'],
            'image_width': userdata['image_width']
        }
        with open(outputs['parameters'][0]['resource_path'], 'w') as g:
            json.dump(parameters, g)

    def test_my_task(self, testcase):
        inputs = {
            'image': [{'large_thumb_url': '/fake/url',
                       'small_thumb_url': '/fake/url',}]
        }
        settings = {}
        outputs = {
            'parameters': [{'resource_type': 'application/json',
                            'resource_path': testcase.new_available_path()}]
        }

        try:
            self.get_my_interface(inputs, settings)
        except Exception as e:
            testcase.fail('get_my_interface() raises an exception: {0}'.format(str(e)))

        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'cc_size': 15})
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'cc_size': 15, 'image_width': 'aaa'})
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'cc_size': 15, 'image_width': 10.50})
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'cc_size': 15, 'image_width': -10})
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'cc_size': -15, 'image_width': 1000})
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'cc_size': 1.5, 'image_width': 1000})

        userdata = {'cc_size': 15, 'image_width': 1000}
        self.save_my_user_input(inputs, settings, outputs, userdata)
        with open(outputs['parameters'][0]['resource_path'], 'r') as f:
            testcase.assertEqual(json.load(f), userdata)


class ApplyDespeckleTask(RodanAutomaticTask):
    name = '{0}_apply_despeckle'.format(str(fn))
    author = "Ling-Xiao Yang"
    description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = {}
    enabled = True
    category = rdn_despeckle.module.category

    input_port_types = [{
        'name': 'image',
        'resource_types': i_type['resource_types'],
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
        'resource_types': o_type['resource_types'],
        'minimum': 1,
        'maximum': 1
    }]

    def run_my_task(self, inputs, rodan_job_settings, outputs):
        task_image = load_image(inputs['image'][0]['resource_path'])
        with open(inputs['parameters'][0]['resource_path']) as f:
            parameters = json.load(f)
        result_image = task_image.rdn_despeckle(**parameters)
        result_image = ensure_pixel_type(result_image, outputs['output'][0]['resource_type'])
        result_image.save_PNG(outputs['output'][0]['resource_path'])
