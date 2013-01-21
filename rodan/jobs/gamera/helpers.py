import os
import uuid
import tempfile
import shutil
from django.core.files import File
from celery import Task
from celery import registry
from rodan.models.job import Job
from rodan.models.result import Result
import gamera.core


class GameraTask(Task):
    module_fn = None
    module_settings = []
    workflowjob_obj = None

    def run(self, job_data, *args, **kwargs):
        # initialize the outgoing result object so we can update it as we go.
        new_task_result = Result(
            page=job_data['previous_result'].page,
            workflow_job=self.workflowjob_obj
        )
        new_task_result.save()
        result_save_path = new_task_result.result_path

        # parse the module settings
        settings = {}
        for s in self.module_settings:
            setting_name = "_".join(s['name'].split(" "))
            setting_value = s['default']
            settings[setting_name] = setting_value

        gamera.core.init_gamera()  # initialize Gamera in the task
        task_image = gamera.core.load_image(job_data['previous_result'].result.path)

        tdir = tempfile.mkdtemp()
        # perform the requested task
        task_function = self.name.split(".")[-1]
        result_image = getattr(task_image, task_function)(**settings)
        result_file = "{0}.png".format(uuid.uuid4())
        result_image.save_image(os.path.join(tdir, result_file))

        f = open(os.path.join(tdir, result_file))
        new_task_result.result.save(os.path.join(result_save_path, result_file), File(f))
        f.close()
        shutil.rmtree(tdir)

        # this will format the output of this task in such a way that
        # it can be chained together with another instance of a GameraTask
        res = {
            'previous_result': new_task_result
        }
        return res


class GameraInteractiveTask(Task):
    module_fn = None
    module_settings = []
    workflowjob_obj = None

    def run(self, job_data, *args, **kwargs):
        pass


def convert_arg_list(arglist):
    if not arglist:
        return None
    ret = []
    for a in arglist:
        arg = a.__dict__
        if 'klass' in arg.keys():
            del arg['klass']

        # so we don't have to use Gamera's NoneType
        if str(arg['default']) == 'None':
            arg['default'] = None
        ret.append(arg)
    return ret


def convert_input_type(input_type):
    dict_repr = input_type.__dict__
    if 'klass' in dict_repr.keys():
        del dict_repr['klass']
    return dict_repr


def convert_output_type(output_type):
    dict_repr = output_type.__dict__
    if 'klass' in dict_repr.keys():
        del dict_repr['klass']
    return dict_repr


def create_jobs_from_module(gamera_module):
    previously_loaded_modules = Job.objects.values_list('name', flat=True)
    for fn in gamera_module.module.functions:
        if not fn.return_type:
            continue

        module_task = GameraTask()
        module_task.name = str(fn)
        module_task.module_fn = fn
        registry.tasks.register(module_task)

        # skip the job creation if we've already
        # stored a reference to this job in the database
        if str(fn) in previously_loaded_modules:
            continue

        input_types = convert_input_type(fn.self_type)
        output_types = convert_output_type(fn.return_type)
        arguments = convert_arg_list(fn.args.list)

        j = Job(
            name=str(fn),
            author=fn.author,
            input_types=input_types,
            output_types=output_types,
            arguments=arguments,
            enabled=True,
            category=gamera_module.module.category
        )
        j.save()
