import json, jsonschema
from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import ImageDraw
from rodan.jobs.base import RodanTask
from rodan.jobs.gamera import argconvert
from gamera.plugins.threshold import threshold

fn = threshold
i_type = argconvert.convert_input_type(fn.self_type)
o_type = argconvert.convert_output_type(fn.return_type)

class SimpleBinariseInteractive(RodanTask):
    name = 'gamera.custom.simple_binarise_interactive'
    author = "Ling-Xiao Yang"
    description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = {}
    enabled = True
    category = fn.module.category
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
        if '@threshold' not in settings:
            return self.WAITING_FOR_INPUT()
        else:
            task_image = load_image(inputs['input'][0]['resource_path'])
            result_image = task_image.threshold(threshold=settings['@threshold'],
                                                storage_format=0) # no compression
            result_image.save_PNG(outputs['output'][0]['resource_path'])

    def get_my_interface(self, inputs, settings):
        t = 'interfaces/simple_binarise.html'
        c = {
            'large_thumb_url': inputs['input'][0]['large_thumb_url'],
            'small_thumb_url': inputs['input'][0]['small_thumb_url'],
        }
        return (t, c)

    # [TODO] interface submit JSON instead of form-data
    #validator = jsonschema.Draft4Validator({
    #    "type": "object",
    #    "required": ["threshold"],
    #    "properties": {
    #        "threshold": {
    #            "type": "integer",
    #            "minimum": 0   # inclusive
    #        }
    #    }
    #})
    def validate_my_user_input(self, inputs, settings, user_input):
        #try:
        #    self.validator.validate(user_input)
        #except jsonschema.exceptions.ValidationError as e:
        #    raise self.ManualPhaseException(e.message)
        if 'threshold' not in user_input:
            raise self.ManualPhaseException("Threshold is required.")
        threshold = user_input['threshold']
        try:
            val = int(threshold)
        except (TypeError, ValueError):
            raise self.ManualPhaseException("Invalid threshold")

        return {
            '@threshold': val
        }

    def test_my_task(self, testcase):
        inputs = {
            'input': [{'resource_type': 'image/greyscale+png',
                       'resource_path': testcase.new_available_path(),
                       'large_thumb_url': '/fake/url',
                       'small_thumb_url': '/fake/url'}]
        }
        from PIL import Image
        Image.new("RGBA", size=(50, 50), color=(256, 0, 0)).save(inputs['input'][0]['resource_path'], 'png')
        im = load_image(inputs['input'][0]['resource_path'])
        im = im.to_greyscale()
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

        testcase.assertRaises(self.ManualPhaseException, self.validate_my_user_input, inputs, settings, {'threshold': None})

        user_input = {'threshold': 128}
        settings_update = self.validate_my_user_input(inputs, settings, user_input)
        testcase.assertEqual(settings_update, {
            '@threshold': 128,
        })

        # Automatic Phase
        settings.update(settings_update)
        retval = self.run_my_task(inputs, settings, outputs)
        testcase.assertNotEqual(type(retval), self.WAITING_FOR_INPUT)
