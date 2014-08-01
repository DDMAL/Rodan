from celery import registry
from rodan.jobs.gamera.celery_task import GameraTask
from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from rodan.settings import IMAGE_TYPES
from rodan.jobs.gamera import argconvert


def create_jobs_from_module(gamera_module, interactive=False):
    previously_loaded_modules = list(Job.objects.values_list('job_name', 'interactive'))

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

        module_task = GameraTask()
        module_task.name = str(fn)
        registry.tasks.register(module_task)

        # skip the job creation if we've already
        # stored a reference to this job in the database
        if (str(fn), interactive) in previously_loaded_modules:
            continue

        input_types = []
        for t in self_type:
            input_types.append(argconvert.convert_input_type(t))

        output_types = []
        for t in return_type:
            output_types.append(argconvert.convert_output_type(t))

        settings = argconvert.convert_arg_list(fn.args.list)

        j = Job(
            job_name=str(fn),
            author=fn.author,
            description=fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"'),
            settings=settings,
            enabled=True,
            category=gamera_module.module.category,
            interactive=interactive
        )

        j.save()

        for t in input_types:
            ipt = InputPortType(job=j,
                                name=t['name'],
                                resource_type=t['pixel_types'],
                                minimum=1,
                                maximum=1)
            ipt.save()

        for t in output_types:
            opt = OutputPortType(job=j,
                                 name=t['name'],
                                 resource_type=t['pixel_types'],
                                 minimum=1,
                                 maximum=1)
            opt.save()

        previously_loaded_modules += [(str(fn), interactive)]
