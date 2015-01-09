from gamera.core import init_gamera, load_image
from gamera import enums
from rodan.jobs.gamera import argconvert
from rodan.jobs.base import RodanAutomaticTask

def load_gamera_module(gamera_module):
    for fn in gamera_module.module.functions:
        # we only want jobs that will return a result and has a known pixel type
        if not fn.return_type:
            continue

        if "pixel_types" not in fn.return_type.__dict__.keys():
            continue

        i_type = argconvert.convert_input_type(fn.self_type)
        if len(i_type['resource_types']) == 0:  # it deals with FLOAT and COMPLEX pixel types only -- we don't support them in Rodan
            continue
        input_types = [{
            'name': "input",
            'resource_types': i_type['resource_types'],
            'minimum': 1,
            'maximum': 1,
        }]

        o_type = argconvert.convert_output_type(fn.return_type)
        if len(o_type['resource_types']) == 0:  # it deals with FLOAT and COMPLEX pixel types only -- we don't support them in Rodan
            continue
        output_types = [{
            'name': "output",
            'resource_types': o_type['resource_types'],
            'minimum': 1,
            'maximum': 1,
        }]

        try:
            settings_schema = argconvert.convert_arg_list(fn.args.list)
        except TypeError:  # we now exclude the function with argument <ImageType>
            continue

        class gamera_module_task(RodanAutomaticTask):
            name = str(fn)
            author = fn.author
            description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
            settings = settings_schema
            enabled = True
            category = gamera_module.module.category
            input_port_types = input_types
            output_port_types = output_types

            def run_my_task(self, inputs, rodan_job_settings, outputs):
                settings = argconvert.convert_to_gamera_settings(rodan_job_settings)
                task_image = load_image(inputs['input'][0]['resource_path'])
                task_function = self.name.split(".")[-1]
                result_image = getattr(task_image, task_function)(**settings)
                result_image = ensure_pixel_type(result_image, outputs['output'][0]['resource_type'])
                result_image.save_PNG(outputs['output'][0]['resource_path'])

            def test_my_task(self, testcase):
                inputs = {
                    'input': [{'resource_type': None,  # should be filled in later
                              'resource_path': testcase.new_available_path()}]
                }
                outputs = {
                    'output': [{'resource_type': None,  # should be filled in later
                               'resource_path': testcase.new_available_path()}]
                }

                if self.name == "gamera.plugins.image_conversion.to_greyscale":
                    from PIL import Image
                    Image.new("RGBA", size=(50, 50), color=(256, 0, 0)).save(inputs['input'][0]['resource_path'], 'png')
                    inputs['input'][0]['resource_type'] = 'image/rgb+png'
                    outputs['output'][0]['resource_type'] = 'image/greyscale+png'
                    self.run_my_task(inputs, {}, outputs)
                    im = Image.open(outputs['output'][0]['resource_path'])
                    testcase.assertEqual(im.mode, 'L')
                elif self.name == "gamera.plugins.binarization.niblack_threshold":
                    # test incompatible type
                    from PIL import Image
                    Image.new("RGBA", size=(50, 50), color=(256, 0, 0)).save(inputs['input'][0]['resource_path'], 'png')
                    inputs['input'][0]['resource_type'] = 'image/rgb+png'
                    outputs['output'][0]['resource_type'] = 'image/onebit+png'
                    testcase.assertRaises(TypeError, self.run_my_task, inputs, {}, outputs)
                else:
                    # [TODO] for other Gamera tasks
                    pass

def ensure_pixel_type(gamera_image, mimetype):
    target_type = argconvert.convert_mimetype_to_pixel(mimetype)
    if target_type != gamera_image.data.pixel_type:
        if target_type == enums.ONEBIT:
            return gamera_image.to_onebit()
        elif target_type == enums.GREYSCALE:
            return gamera_image.to_greyscale()
        elif target_type == enums.GREY16:
            return gamera_image.to_grey16()
        elif target_type == enums.RGB:
            return gamera_image.to_rgb()
        elif target_type == enums.FLOAT:
            return gamera_image.to_float()
        elif target_type == enums.COMPLEX:
            return gamera_image.to_complex()
        else:
            raise TypeError('Unsupported Gamera type: {0}'.format(target_type))
    else:
        return gamera_image
