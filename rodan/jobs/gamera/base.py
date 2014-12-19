from gamera.core import init_gamera, load_image
from rodan.jobs.gamera import argconvert
from rodan.jobs.base import RodanAutomaticTask

def load_gamera_module(gamera_module):
    for fn in gamera_module.module.functions:
        # we only want jobs that will return a result and has a known pixel type
        if not fn.return_type:
            continue

        if "pixel_types" not in fn.return_type.__dict__.keys():
            continue

        if not hasattr(fn.self_type, '__iter__'):
            self_type = (fn.self_type, )
        else:
            self_type = fn.self_type

        if not hasattr(fn.return_type, '__iter__'):
            return_type = (fn.return_type, )
        else:
            return_type = fn.return_type

        input_types = []
        for i, t in enumerate(self_type):
            tc = argconvert.convert_input_type(t)
            input_types.append({
                'name': tc['name'] or "input-{0}".format(i),
                'resource_types': map(argconvert.convert_pixel_to_mimetype, tc['pixel_types']),
                'minimum': 1,
                'maximum': 1,
            })

        output_types = []
        for i, t in enumerate(return_type):
            tc = argconvert.convert_input_type(t)
            output_types.append({
                'name': tc['name'] or "output-{0}".format(i),
                'resource_types': map(argconvert.convert_pixel_to_mimetype, tc['pixel_types']),
                'minimum': 1,
                'maximum': 1,
            })

        class gamera_module_task(RodanAutomaticTask):
            name = str(fn)
            author = fn.author
            description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
            settings = argconvert.convert_arg_list(fn.args.list)
            enabled = True
            category = gamera_module.module.category
            input_port_types = input_types
            output_port_types = output_types

            def run_my_task(self, inputs, rodan_job_settings, outputs):
                settings = argconvert.convert_to_gamera_settings(rodan_job_settings)
                task_image = load_image(inputs[inputs.keys()[0]][0]['resource_path'])
                task_function = self.name.split(".")[-1]
                result_image = getattr(task_image, task_function)(**settings)
                result_image.save_image(outputs[outputs.keys()[0]][0]['resource_path'])

            def test_my_task(self, testcase):
                inputs = {}
                for ipt_desc in input_types:
                    ipt = ipt_desc['name']
                    inputs[ipt] = [
                        {'resource_type': None,  # should be filled in later
                         'resource_path': testcase.new_available_path()}
                    ]
                outputs = {}
                for opt_desc in output_types:
                    opt = opt_desc['name']
                    outputs[opt] = [
                        {'resource_type': None,  # should be filled in later
                         'resource_path': testcase.new_available_path()}
                    ]

                if self.name == "gamera.plugins.image_conversion.to_greyscale":
                    from PIL import Image
                    Image.new("RGBA", size=(50, 50), color=(256, 0, 0)).save(inputs['input-0'][0]['resource_path'], 'png')
                    inputs['input-0'][0]['resource_type'] = 'image/rgb+png'
                    outputs['float'][0]['resource_type'] = 'image/float+png'
                    self.run_my_task(inputs, {}, outputs)
                    im = Image.open(outputs['float'][0]['resource_path'])
                    testcase.assertEqual(im.mode, 'L')
                elif self.name == "gamera.plugins.binarization.niblack_threshold":
                    # test incompatible type
                    from PIL import Image
                    Image.new("RGBA", size=(50, 50), color=(256, 0, 0)).save(inputs['input-0'][0]['resource_path'], 'png')
                    inputs['input-0'][0]['resource_type'] = 'image/rgb+png'
                    outputs['onebit'][0]['resource_type'] = 'image/onebit+png'
                    testcase.assertRaises(TypeError, self.run_my_task, inputs, {}, outputs)
                else:
                    # [TODO] for other Gamera tasks
                    pass
