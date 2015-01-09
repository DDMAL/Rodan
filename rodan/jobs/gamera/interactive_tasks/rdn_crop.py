import json
import jsonschema
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import ImageDraw
from rodan.jobs.base import RodanAutomaticTask, RodanManualTask, ManualJobException
from rodan.jobs.gamera import argconvert
from rodan.jobs.gamera.base import ensure_pixel_type
from gamera.toolkits.rodan_plugins.plugins.rdn_crop import rdn_crop
from django.template.loader import get_template

fn = rdn_crop.module.functions[0]
i_type = argconvert.convert_input_type(fn.self_type)
o_type = argconvert.convert_output_type(fn.return_type)

class ManualCropTask(RodanManualTask):
    name = '{0}_manual'.format(str(fn))
    author = "Ling-Xiao Yang"
    description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = {}
    enabled = True
    category = rdn_crop.module.category

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
        t = get_template('gamera/interfaces/rdn_crop.html')
        c = {
            'image_url': inputs['image'][0]['large_thumb_url'],
        }
        return (t, c)

    validator = jsonschema.Draft4Validator({
        "type": "object",
        "required": ["ulx", "uly", "lrx", "lry", "imw"],
        "properties": {
            "ulx": {"type": "number"},
            "uly": {"type": "number"},
            "lrx": {"type": "number"},
            "lry": {"type": "number"},
            "imw": {
                "description": "thumbnail image width",
                "type": "integer",
                "minimum": 0
            }
        }
    })
    def save_my_user_input(self, inputs, settings, outputs, userdata):
        try:
            self.validator.validate(userdata)
        except jsonschema.exceptions.ValidationError as e:
            raise ManualJobException(e.message)
        parameters = {
            'ulx': userdata['ulx'],
            'uly': userdata['uly'],
            'lrx': userdata['lrx'],
            'lry': userdata['lry'],
            'imw': userdata['imw']
        }
        with open(outputs['parameters'][0]['resource_path'], 'w') as g:
            json.dump(parameters, g)
    def test_my_task(self, testcase):
        inputs = {
            'image': [{'large_thumb_url': '/fake/url'}]
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

        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'ulx': 2.2})
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'ulx': 2.2, 'uly': 2.3})
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'ulx': 2.2, 'uly': 2.3, 'lrx': 2.5})
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'ulx': 2.2, 'uly': 2.3, 'lrx': 2.5, 'lry': 3.5})
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'ulx': 2.2, 'uly': 2.3, 'lrx': 2.5, 'lry': 3.5, 'imw': 'hahaha'})
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'ulx': 2.2, 'uly': 2.3, 'lrx': 2.5, 'lry': 3.5, 'imw': 123.5})
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'ulx': 2.2, 'uly': 2.3, 'lrx': 2.5, 'lry': 3.5, 'imw': -1})

        userdata = {'ulx': 2.2, 'uly': 2.3, 'lrx': 2.5, 'lry': 3.5, 'imw': 1500}
        self.save_my_user_input(inputs, settings, outputs, userdata)
        with open(outputs['parameters'][0]['resource_path'], 'r') as f:
            testcase.assertEqual(json.load(f), userdata)


class ApplyCropTask(RodanAutomaticTask):
    name = '{0}_apply_crop'.format(str(fn))
    author = "Ling-Xiao Yang"
    description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = {}
    enabled = True
    category = rdn_crop.module.category

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
        result_image = task_image.rdn_crop(**parameters)
        result_image = ensure_pixel_type(result_image, outputs['output'][0]['resource_type'])
        result_image.save_PNG(outputs['output'][0]['resource_path'])

    def test_my_task(self, testcase):
        inputs = {
            'image': [{'resource_type': 'image/rgb+png',
                       'resource_path': testcase.new_available_path()}],
            'parameters': [{'resource_type': 'application/json',
                            'resource_path': testcase.new_available_path()}]
        }
        settings = {}
        outputs = {
            'output': [{'resource_type': 'image/rgb+png',
                       'resource_path': testcase.new_available_path()}]
        }
        from PIL import Image
        Image.new("RGBA", size=(50, 50), color=(256, 0, 0)).save(inputs['image'][0]['resource_path'], 'png')
        with open(inputs['parameters'][0]['resource_path'], 'w') as g:
            json.dump({'ulx': 2, 'uly': 2, 'lrx': 4, 'lry': 4, 'imw': 25}, g)

        self.run_my_task(inputs, settings, outputs)
        im = Image.open(outputs['output'][0]['resource_path'])
        testcase.assertEqual(im.size, (4, 4))
