import json
import jsonschema
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import ImageDraw
from rodan.jobs.base import RodanTask
from rodan.jobs.gamera import argconvert
from rodan.jobs.gamera.base import ensure_pixel_type
from gamera.toolkits.rodan_plugins.plugins.rdn_crop import rdn_crop
from django.template.loader import get_template

fn = rdn_crop.module.functions[0]
i_type = argconvert.convert_input_type(fn.self_type)
o_type = argconvert.convert_output_type(fn.return_type)

class RdnCrop(RodanTask):
    name = '{0}'.format(str(fn))
    author = "Ling-Xiao Yang"
    description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = {}
    enabled = True
    category = rdn_crop.module.category
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
        if '@ulx' not in settings or '@uly' not in settings or '@lrx' not in settings or '@lry' not in settings or '@imw' not in settings:
            return self.WAITING_FOR_INPUT()
        else:
            task_image = load_image(inputs['input'][0]['resource_path'])
            result_image = task_image.rdn_crop(ulx=settings['@ulx'],
                                               uly=settings['@uly'],
                                               lrx=settings['@lrx'],
                                               lry=settings['@lry'],
                                               imw=settings['@imw'])
            result_image = ensure_pixel_type(result_image, outputs['output'][0]['resource_type'])
            result_image.save_PNG(outputs['output'][0]['resource_path'])

    def get_my_interface(self, inputs, settings):
        t = get_template('gamera/interfaces/rdn_crop.html')
        c = {
            'image_url': inputs['input'][0]['large_thumb_url'],
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
    def validate_my_user_input(self, inputs, settings, user_input):
        try:
            self.validator.validate(user_input)
        except jsonschema.exceptions.ValidationError as e:
            raise self.ManualPhaseException(e.message)

        return {
            '@ulx': user_input['ulx'],
            '@uly': user_input['uly'],
            '@lrx': user_input['lrx'],
            '@lry': user_input['lry'],
            '@imw': user_input['imw']
        }

    def test_my_task(self, testcase):
        inputs = {
            'input': [{'resource_type': 'image/rgb+png',
                       'resource_path': testcase.new_available_path(),
                       'large_thumb_url': '/fake/url'}]
        }
        from PIL import Image
        Image.new("RGBA", size=(50, 50), color=(256, 0, 0)).save(inputs['input'][0]['resource_path'], 'png')

        settings = {}
        outputs = {
            'output': [{'resource_type': 'image/rgb+png',
                        'resource_path': testcase.new_available_path()}]
        }

        # Manual Phase
        retval = self.run_my_task(inputs, settings, outputs)
        testcase.assertEqual(type(retval), self.WAITING_FOR_INPUT)

        try:
            self.get_my_interface(inputs, settings)
        except Exception as e:
            testcase.fail('get_my_interface() raises an exception: {0}'.format(str(e)))

        testcase.assertRaises(self.ManualPhaseException, self.validate_my_user_input, inputs, settings, {'ulx': 2.2})
        testcase.assertRaises(self.ManualPhaseException, self.validate_my_user_input, inputs, settings, {'ulx': 2.2, 'uly': 2.3})
        testcase.assertRaises(self.ManualPhaseException, self.validate_my_user_input, inputs, settings, {'ulx': 2.2, 'uly': 2.3, 'lrx': 2.5})
        testcase.assertRaises(self.ManualPhaseException, self.validate_my_user_input, inputs, settings, {'ulx': 2.2, 'uly': 2.3, 'lrx': 2.5, 'lry': 3.5})
        testcase.assertRaises(self.ManualPhaseException, self.validate_my_user_input, inputs, settings, {'ulx': 2.2, 'uly': 2.3, 'lrx': 2.5, 'lry': 3.5, 'imw': 'hahaha'})
        testcase.assertRaises(self.ManualPhaseException, self.validate_my_user_input, inputs, settings, {'ulx': 2.2, 'uly': 2.3, 'lrx': 2.5, 'lry': 3.5, 'imw': 123.5})
        testcase.assertRaises(self.ManualPhaseException, self.validate_my_user_input, inputs, settings, {'ulx': 2.2, 'uly': 2.3, 'lrx': 2.5, 'lry': 3.5, 'imw': -1})

        user_input = {'ulx': 2, 'uly': 2, 'lrx': 4, 'lry': 4, 'imw': 25, 'haha': 'hahaha'}
        settings_update = self.validate_my_user_input(inputs, settings, user_input)
        testcase.assertEqual(settings_update, {
            '@ulx': 2,
            '@uly': 2,
            '@lrx': 4,
            '@lry': 4,
            '@imw': 25
        })

        # Automatic Phase
        settings.update(settings_update)
        retval = self.run_my_task(inputs, settings, outputs)
        testcase.assertNotEqual(type(retval), self.WAITING_FOR_INPUT)
        im = Image.open(outputs['output'][0]['resource_path'])
        testcase.assertEqual(im.size, (4, 4))
