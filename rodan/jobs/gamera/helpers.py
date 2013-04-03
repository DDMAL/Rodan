import os
import uuid
import tempfile
import shutil
from django.core.files import File
from celery import Task
from celery import registry
from rodan.models.job import Job
from rodan.models.runjob import RunJob
from rodan.models.result import Result
from rodan.jobs.gamera import argconvert
from gamera.core import init_gamera, load_image
# from rodan.models.workflowjob import WorkflowJob


class GameraTask(Task):
    max_retries = None

    def run(self, result_id, runjob_id, *args, **kwargs):
        print "RUNJOB UUID: {0}".format(runjob_id)
        print "RUNJOB RESULT: {0}".format(result_id)

        runjob = RunJob.objects.get(pk=runjob_id)

        # fall through to retrying if we're waiting for input
        if runjob.needs_input:
            print "RUNJOB NEEDS INPUT"
            self.retry(args=[result_id, runjob_id], countdown=10, *args, **kwargs)

        if result_id is None:
            # this is the first job in a run
            print "Compat File Path: {0}".format(runjob.page.compat_file_path)
            page = runjob.page.compat_file_path
        else:
            # we take the page image we want to operate on from the previous result object
            result = Result.objects.get(pk=result_id)
            page = result.result.path

        new_result = Result(run_job=runjob)
        new_result.save()

        result_save_path = new_result.result_path
        print "RESULT SAVE PATH {0}".format(result_save_path)

        settings = {}
        for s in runjob.job_settings:
            setting_name = "_".join(s['name'].split(" "))
            setting_value = argconvert.convert_to_arg_type(s['type'], s['default'])
            settings[setting_name] = setting_value

        init_gamera()

        task_image = load_image(page)
        tdir = tempfile.mkdtemp()
        task_function = self.name.split(".")[-1]
        result_image = getattr(task_image, task_function)(**settings)
        result_file = "{0}.png".format(str(uuid.uuid4()))
        result_image.save_image(os.path.join(tdir, result_file))

        print "Temporary File {0}".format(os.path.join(tdir, result_file))

        f = open(os.path.join(tdir, result_file))
        new_result.result.save(os.path.join(result_save_path, result_file), File(f))
        f.close()
        shutil.rmtree(tdir)

        print "New Result: {0}".format(str(new_result.uuid))
        return str(new_result.uuid)

        # current_wf_job = WorkflowJob.objects.get(uuid=job_data['current_wf_job_uuid'])

        # if current_wf_job.needs_input:
        #     self.retry(job_data=job_data)
        # else:
        #     workflow = current_wf_job.workflow
        #     previous_wf_job = workflow.previous_job(wf_job=current_wf_job, page=current_wf_job.page)

        #     if previous_wf_job is None:
        #         # this is the first task in the workflow
        #         path_to_image = current_wf_job.page.compat_file_path
        #     else:
        #         path_to_image = previous_wf_job.result_set.all()[0].result.path

        #     # initialize the outgoing result object so we can update it as we go.
        #     new_task_result = Result(
        #         workflow_job=current_wf_job,
        #         task_name=self.name
        #     )
        #     new_task_result.save()
        #     result_save_path = new_task_result.result_path

        #     # parse the module settings
        #     settings = {}

        #     for s in current_wf_job.job_settings:
        #         setting_name = "_".join(s['name'].split(" "))
        #         setting_value = argconvert.convert_to_arg_type(s['type'], s['default'])
        #         settings[setting_name] = setting_value

        #     init_gamera()  # initialize Gamera in the task
        #     task_image = load_image(path_to_image)

        #     tdir = tempfile.mkdtemp()
        #     # perform the requested task
        #     task_function = self.name.split(".")[-1]
        #     result_image = getattr(task_image, task_function)(**settings)
        #     result_file = "{0}.png".format(uuid.uuid4())
        #     result_image.save_image(os.path.join(tdir, result_file))

        #     f = open(os.path.join(tdir, result_file))

        #     new_task_result.result.save(os.path.join(result_save_path, result_file), File(f))
        #     f.close()
        #     shutil.rmtree(tdir)

        #     next_wf_job = workflow.next_job(wf_job=current_wf_job, page=current_wf_job.page)
        #     out = {
        #         'current_wf_job_uuid': next_wf_job.uuid if next_wf_job is not None else None
        #     }
        #     return out

    # def try_again(self, result, runjob_id, *args, **kwargs):
    #     # do something like this
    #     print "ARGS: {0}".format(args)
    #     print "KWARGS: {0}".format(kwargs)
    #     self.retry(args=[result, runjob_id], *args, **kwargs)
    def on_success(self, retval, task_id, args, kwargs):
        print "Task Was Successful"

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        print "After Return!!"


def create_jobs_from_module(gamera_module, interactive=False):
    previously_loaded_modules = Job.objects.values_list('job_name', flat=True)
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
        if str(fn) in previously_loaded_modules:
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
