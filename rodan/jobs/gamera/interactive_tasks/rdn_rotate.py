from gamera.core import load_image
from gamera.plugins.pil_io import from_pil
from PIL import ImageDraw
from rodan.jobs.base import RodanAutomaticTask, RodanManualTask, ManualJobException
from rodan.jobs.gamera import argconvert
from rodan.jobs.gamera.base import ensure_pixel_type
from gamera.toolkits.rodan_plugins.plugins.rdn_rotate import rdn_rotate
from django.template.loader import get_template

fn = rdn_rotate.module.functions[0]
i_type = argconvert.convert_input_type(fn.self_type)
o_type = argconvert.convert_output_type(fn.return_type)

class ManualRotateTask(RodanManualTask):
    name = '{0}_manual'.format(str(fn))
    author = "Ling-Xiao Yang"
    description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = {}
    enabled = True
    category = rdn_rotate.module.category

    input_port_types = [{
        'name': 'image',
        'resource_types': i_type['resource_types'],
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
            raise ManualJobException("Angle is required.")
        angle = userdata['angle']
        try:
            val = float(angle)
        except ValueError:
            raise ManualJobException("Invalid angle")

        with open(outputs['angle'][0]['resource_path'], 'w') as g:
            g.write(str(val))

    def test_my_task(self, testcase):
        inputs = {
            'image': [{'large_thumb_url': '/fake/url'}]
        }
        settings = {}
        outputs = {
            'angle': [{'resource_type': 'text/plain',
                            'resource_path': testcase.new_available_path()}]
        }

        try:
            self.get_my_interface(inputs, settings)
        except Exception as e:
            testcase.fail('get_my_interface() raises an exception: {0}'.format(str(e)))

        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'hahaha': 'hahaha'})
        testcase.assertRaises(ManualJobException, self.save_my_user_input, inputs, settings, outputs, {'angle': 'hahaha'})
        self.save_my_user_input(inputs, settings, outputs, {'angle': 15.6})
        with open(outputs['angle'][0]['resource_path'], 'r') as f:
            testcase.assertEqual(f.read(), '15.6')



class ApplyRotateTask(RodanAutomaticTask):
    name = '{0}_apply_rotate'.format(str(fn))
    author = "Ling-Xiao Yang"
    description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
    settings = {}
    enabled = True
    category = rdn_rotate.module.category

    input_port_types = [{
        'name': 'image',
        'resource_types': i_type['resource_types'],
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
        'resource_types': o_type['resource_types'],
        'minimum': 1,
        'maximum': 1
    }]

    def run_my_task(self, inputs, rodan_job_settings, outputs):
        task_image = load_image(inputs['image'][0]['resource_path'])
        with open(inputs['angle'][0]['resource_path']) as f:
            angle = float(f.read())
        result_image = task_image.rdn_rotate(angle)
        result_image = ensure_pixel_type(result_image, outputs['output'][0]['resource_type'])
        result_image.save_PNG(outputs['output'][0]['resource_path'])
