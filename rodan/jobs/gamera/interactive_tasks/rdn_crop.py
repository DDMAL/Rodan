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
    settings = []
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
            "imw": {"type": "number"}
        }
    })
    def save_my_user_input(self, inputs, settings, outputs, userdata):
        try:
            self.validator.validate(userdata) ## TODO: userdata
        except jsonschema.exceptions.ValidationError as e:
            raise ManualJobException(e.message)
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
    def test_my_task(self, testcase):
        inputs = {}
        settings = {}
        outputs = {
            'parameters': [{'resource_type': 'application/json',
                            'resource_path': testcase.new_available_path()}]
        }
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'ulx': 2.2})
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'ulx': 2.2, 'uly': 2.3})
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'ulx': 2.2, 'uly': 2.3, 'lrx': 2.5})
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'ulx': 2.2, 'uly': 2.3, 'lrx': 2.5, 'lry': 3.5})
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'ulx': 2.2, 'uly': 2.3, 'lrx': 2.5, 'lry': 3.5, 'imw': 'hahaha'})

        userdata = {'ulx': 2.2, 'uly': 2.3, 'lrx': 2.5, 'lry': 3.5, 'imw': 1500}
        self.save_my_user_input(inputs, settings, outputs, userdata)
        with open(outputs['parameters'][0]['resource_path'], 'r') as f:
            testcase.assertEqual(json.load(f), userdata)


class ApplyCropTask(RodanAutomaticTask):
    name = '{0}_apply_crop'.format(str(fn))
    author = "Ling-Xiao Yang"
    description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = []
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
