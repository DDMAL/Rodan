import json, jsonschema
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import ImageDraw
from rodan.jobs.base import RodanTask
from rodan.jobs.gamera import argconvert
from rodan.jobs.gamera.base import ensure_pixel_type
from gamera.toolkits.rodan_plugins.plugins.rdn_despeckle import rdn_despeckle
from django.template.loader import get_template

fn = rdn_despeckle.module.functions[0]
i_type = argconvert.convert_input_type(fn.self_type)
o_type = argconvert.convert_output_type(fn.return_type)

class RdnDespeckle(RodanTask):
    name = '{0}_interactive'.format(str(fn))
    author = "Ling-Xiao Yang"
    description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = {}
    enabled = True
    category = rdn_despeckle.module.category
    interactive = True

    input_port_types = [{
        'name': 'input',
        'resource_types': i_type['resource_types'],
        'minimum': 1,
        'maximum': 1
    }]
    output_port_types = [{
        'name': 'output',
        'resource_types': o_type['resource_types'],
        'minimum': 1,
        'maximum': 1
    }]

    def run_my_task(self, inputs, settings, outputs):
        if '@cc_size' not in settings or '@image_width' not in settings:
            return self.WAITING_FOR_INPUT()
        else:
            task_image = load_image(inputs['input'][0]['resource_path'])
            result_image = task_image.rdn_despeckle(cc_size=settings['@cc_size'],
                                                    image_width=settings['@image_width'])
            result_image = ensure_pixel_type(result_image, outputs['output'][0]['resource_type'])
            result_image.save_PNG(outputs['output'][0]['resource_path'])

    def get_my_interface(self, inputs, settings):
        t = get_template('gamera/interfaces/rdn_despeckle.html')
        c = {
            'image_url_large': inputs['input'][0]['large_thumb_url'],
            'image_url_small': inputs['input'][0]['small_thumb_url'],
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
    def validate_my_user_input(self, inputs, settings, user_input):
        try:
            self.validator.validate(user_input)
        except jsonschema.exceptions.ValidationError as e:
            raise self.ManualPhaseException(e.message)

        return {
            '@cc_size': user_input['cc_size'],
            '@image_width': user_input['image_width']
        }

    def test_my_task(self, testcase):
        inputs = {
            'input': [{'resource_type': 'image/onebit+png',
                       'resource_path': testcase.new_available_path(),
                       'large_thumb_url': '/fake/url',
                       'small_thumb_url': '/fake/url'}]
        }
        from PIL import Image
        Image.new("RGBA", size=(50, 50), color=(256, 0, 0)).save(inputs['input'][0]['resource_path'], 'png')
        im = load_image(inputs['input'][0]['resource_path'])
        im = im.to_onebit()
        im.save_PNG(inputs['input'][0]['resource_path'])

        settings = {}
        outputs = {
            'output': [{'resource_type': 'image/onebit+png',
                        'resource_path': testcase.new_available_path()}]
        }

        # Manual Phase
        retval = self.run_my_task(inputs, settings, outputs)
        testcase.assertEqual(type(retval), self.WAITING_FOR_INPUT)

        try:
            self.get_my_interface(inputs, settings)
        except Exception as e:
            testcase.fail('get_my_interface() raises an exception: {0}'.format(str(e)))

        testcase.assertRaises(self.ManualPhaseException, self.validate_my_user_input, inputs, settings, {'cc_size': 15})
        testcase.assertRaises(self.ManualPhaseException, self.validate_my_user_input, inputs, settings, {'cc_size': 15, 'image_width': 'aaa'})
        testcase.assertRaises(self.ManualPhaseException, self.validate_my_user_input, inputs, settings, {'cc_size': 15, 'image_width': 10.50})
        testcase.assertRaises(self.ManualPhaseException, self.validate_my_user_input, inputs, settings, {'cc_size': 15, 'image_width': -10})
        testcase.assertRaises(self.ManualPhaseException, self.validate_my_user_input, inputs, settings, {'cc_size': -15, 'image_width': 1000})
        testcase.assertRaises(self.ManualPhaseException, self.validate_my_user_input, inputs, settings, {'cc_size': 1.5, 'image_width': 1000})

        user_input = {'cc_size': 15, 'image_width': 1000}
        settings_update = self.validate_my_user_input(inputs, settings, user_input)
        testcase.assertEqual(settings_update, {
            '@cc_size': 15,
            '@image_width': 1000
        })

        # Automatic Phase
        settings.update(settings_update)
        retval = self.run_my_task(inputs, settings, outputs)
        testcase.assertNotEqual(type(retval), self.WAITING_FOR_INPUT)
