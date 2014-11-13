from rodan.jobs.gamera.celery_task import GameraTask
from rodan.jobs.gamera import argconvert


def create_jobs_from_module(gamera_module, interactive=False):
    is_interactive = interactive  # just another name, avoid being masked by class scope below

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
                'name': tc['name'] or "Input Type #{0}".format(i),
                'resource_types': map(pixel_type_to_rodan_type, tc['pixel_types']),
                'minimum': 1,
                'maximum': 1,
            })

        output_types = []
        for i, t in enumerate(return_type):
            tc = argconvert.convert_input_type(t)
            output_types.append({
                'name': tc['name'] or "Output Type #{0}".format(i),
                'resource_types': map(pixel_type_to_rodan_type, tc['pixel_types']),
                'minimum': 1,
                'maximum': 1,
            })

        class gamera_module_task(GameraTask):
            name = str(fn)
            author = fn.author
            description = fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"')
            settings = argconvert.convert_arg_list(fn.args.list)
            enabled = True
            category = gamera_module.module.category
            interactive = is_interactive
            input_port_types = input_types
            output_port_types = output_types


def pixel_type_to_rodan_type(pixel_t):
    # Gamera pixel types can be found in gamera.enums module
    mapp = {
        0: 'image/onebit+png',
        1: 'image/greyscale+png',
        2: 'image/grey16+png',
        3: 'image/rgb+png',
        4: 'image/float+png',
        5: 'image/complex+png',
    }
    return mapp[pixel_t]
