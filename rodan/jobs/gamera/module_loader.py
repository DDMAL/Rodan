from celery import registry
from rodan.jobs.gamera.celery_task import GameraTask
from rodan.models.job import Job
from rodan.jobs.gamera import argconvert


def create_jobs_from_module(gamera_module, interactive=False):
    previously_loaded_modules = Job.objects.values_list('job_name', 'interactive')

    for fn in gamera_module.module.functions:
        # we only want jobs that will return a result and has a known pixel type
        if not fn.return_type:
            continue

        if "pixel_types" not in fn.return_type.__dict__.keys():
            continue

        module_task = GameraTask()
        module_task.name = str(fn)
        registry.tasks.register(module_task)

        # skip the job creation if we've already
        # stored a reference to this job in the database
        if (str(fn), interactive) in previously_loaded_modules:
            continue

        input_types = argconvert.convert_input_type(fn.self_type)
        output_types = argconvert.convert_output_type(fn.return_type)
        settings = argconvert.convert_arg_list(fn.args.list)

        j = Job(
            job_name=str(fn),
            author=fn.author,
            description=fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"'),
            input_types=input_types,
            output_types=output_types,
            settings=settings,
            enabled=True,
            category=gamera_module.module.category,
            interactive=interactive
        )
        j.save()
