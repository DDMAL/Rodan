import os
import uuid
import tempfile
from celery import Task
from celery import registry
from rodan.models.job import Job
import gamera.core


class GameraTask(Task):
    module_fn = None
    module_settings = None
    autoregister = False
    workflow_job_id = None
    page_id = None
    task_seq = 0
    image_path = None

    def run(self, job_data, *args, **kwargs):
        self.image_path = job_data['image_path']
        self.task_seq = job_data['task_seq'] + 1
        self.page_id = job_data['page_id']

        # initialize the result object so we can have it hanging around
        gamera.core.init_gamera()  # initialize Gamera in the task
        task_image = gamera.core.load_image(self.image_path)

        # perform the requested task
        image_fn = self.name.split(".")[-1]
        result_image = getattr(task_image, image_fn)(**self.module_settings)
        result_file = "{0}.tiff".format(uuid.uuid4())
        tempdir = tempfile.gettempdir()
        result_image.save(os.path.join(tempdir, result_file))

        res = {
            'image_path': os.path.join(tempdir, result_file),
            'workflow_job_id': self.workflow_job_id,
            'page_id': self.page_id,
            'task_seq': self.task_seq
        }

        return res


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
    for fn in gamera_module.module.functions:
        if not fn.return_type:
            continue

        module_task = GameraTask()
        module_task.module_fn = fn
        module_task.name = str(fn)
        registry.tasks.register(module_task)

        input_types = convert_input_type(fn.self_type)
        output_types = convert_output_type(fn.return_type)
        arguments = convert_arg_list(fn.args.list)

        j = Job(
            name=str(fn),
            author=fn.author,
            input_types=input_types,
            output_types=output_types,
            arguments=arguments,
            is_enabled=True,
            is_automatic=True,
            is_required=True,
            category=gamera_module.module.category
        )
        j.save()
