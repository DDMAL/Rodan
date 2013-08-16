import os
import uuid
import tempfile
import shutil
from django.core.files import File
from celery import Task
from rodan.models.runjob import RunJob
from rodan.models.runjob import RunJobStatus
from rodan.models.result import Result
from rodan.jobs.gamera import argconvert
from gamera.core import init_gamera, load_image
from rodan.jobs.util import taskutil


class GameraTask(Task):
    max_retries = None
    on_success = taskutil.default_on_success
    on_failure = taskutil.default_on_failure

    def run(self, result_id, runjob_id, *args, **kwargs):
        runjob = RunJob.objects.get(pk=runjob_id)
        taskutil.set_runjob_status(runjob, RunJobStatus.RUNNING)

        # fall through to retrying if we're waiting for input
        if runjob.needs_input:
            runjob = taskutil.set_runjob_status(runjob, RunJobStatus.WAITING_FOR_INPUT)
            self.retry(args=[result_id, runjob_id], *args, countdown=10, **kwargs)

        if runjob.status == RunJobStatus.WAITING_FOR_INPUT:
            runjob = taskutil.set_runjob_status(runjob, RunJobStatus.RUNNING)

        if result_id is None:
            # this is the first job in a run
            page = runjob.page.compat_file_path
        else:
            # we take the page image we want to operate on from the previous result object
            result = Result.objects.get(pk=result_id)
            page = result.result.path

        new_result = Result(run_job=runjob)
        taskutil.save_instance(new_result)

        result_save_path = new_result.result_path

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

        f = open(os.path.join(tdir, result_file))
        taskutil.save_file_field(new_result.result, os.path.join(result_save_path, result_file), File(f))
        f.close()
        shutil.rmtree(tdir)

        return str(new_result.uuid)
