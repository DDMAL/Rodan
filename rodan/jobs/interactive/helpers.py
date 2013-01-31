from celery import Task
from celery import registry
from rodan.models.job import Job
from rodan.jobs.gamera import argconvert


class RodanInteractiveTask(Task):
    max_retries = None
    module_fn = None
    module_settings = []
    workflowjob_obj = None

    # this flag will get set to `False` when the task has
    # received human input and is ready to be run; otherwise
    # it will re-queue itself indefinitely, waiting for more input.
    needs_input = True

    def run(self, job_data, *args, **kwargs):
        if self.needs_input:
            self.retry(job_data)
        else:
            # do stuff
            pass

    def retry(self, job_data, *args, **kwargs):
        # do something like this
        super(RodanInteractiveTask, self).retry(job_data, *args, **kwargs)


def create_interactive_job_from_gamera_function(gamera_fn):
    previously_loaded_modules = Job.objects.values_list('name', flat=True)
    if not gamera_fn.return_type:
        return

    module_task = RodanInteractiveTask()
    module_task.name = str(gamera_fn)
    module_task.module_fn = gamera_fn
    registry.tasks.register(module_task)

    # skip the job creation if we've already
    # stored a reference to this job in the database
    if str(gamera_fn) in previously_loaded_modules:
        return

    input_types = argconvert.convert_input_type(gamera_fn.self_type)

    # we should only ever be using jobs that have an output type.
    # jobs that do not will need to be handled differently.
    output_types = argconvert.convert_output_type(gamera_fn.return_type)
    arguments = argconvert.convert_arg_list(gamera_fn.args.list)

    j = Job(
        name=str(gamera_fn),
        author=gamera_fn.author,
        description=gamera_fn.escape_docstring().replace("\\n", "\n").replace('\\"', '"'),
        input_types=input_types,
        output_types=output_types,
        arguments=arguments,
        enabled=True,
        category=gamera_fn.module.category,
        interactive=True,
    )
    j.save()
