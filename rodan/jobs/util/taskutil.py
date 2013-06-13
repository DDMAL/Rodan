import os
import uuid
import tempfile
import shutil
from django.core.files import File
from rodan.models.runjob import RunJob
from rodan.models.runjob import RunJobStatus
from rodan.models.result import Result
from rodan.jobs.gamera import argconvert
from rodan.helpers.thumbnails import create_thumbnails


def set_running(runjob):
    runjob.status = RunJobStatus.RUNNING
    runjob.save()


def set_run_once_waiting(runjob):
    runjob.status = runjob.status = RunJobStatus.RUN_ONCE_WAITING
    runjob.save()


def init_result(runjob):
    new_result = Result(run_job=runjob)
    new_result.save()
    return new_result


def get_page_url(runjob, result_id):
    if result_id is None:
        # this is the first job in a run
        page = runjob.page.compat_file_path
    else:
        # we take the page image we want to operate on from the previous result object
        result = Result.objects.get(pk=result_id)
        page = result.result.path

    return page


def get_settings(runjob):
    # Note that the runtime value is passed inside the 'default' field.
    settings = {}
    for s in runjob.job_settings:
        setting_name = "_".join(s['name'].split(" "))
        setting_value = argconvert.convert_to_arg_type(s['type'], s['default'])
        settings[setting_name] = setting_value

    return settings


def apply_updates(runjob, updates):
    while updates:
        setting_name, value = updates.popitem()
        for setting in runjob.job_settings:
            if setting['name'] == setting_name:
                setting['default'] = value
    runjob.save()


def create_temp_path(ext=None):
    tdir = tempfile.mkdtemp()
    if ext is None:
        result_file = "{0}".format(str(uuid.uuid4()))
        return os.path.join(tdir, result_file)
    else:
        result_file = "{0}.{1}".format(str(uuid.uuid4()), ext)
        return os.path.join(tdir, result_file)


def save_result(result, result_temp_path):
    # Copy over temp file to appropriate result path, and delete temps.
    # Since the temps are deleted, this method is not indempotent.
    # Best used as a helper method.
    tdir, result_file = os.path.split(result_temp_path)
    result_save_path = result.result_path
    f = open(result_temp_path)
    result.result.save(os.path.join(result_save_path, result_file), File(f))
    f.close()
    shutil.rmtree(tdir)


def save_result_as_png(result_image, runjob):
    temp_path = create_temp_path(ext="png")
    try:
        result_image.save_image(temp_path)
    except AttributeError as e:
        # Debugging
        print "The process_image method probably did not return a valid gamera image."
        print "Did you forget to override process_image or add a return statement?"
        print "Error:"
        print e
    else:
        result = init_result(runjob)
        save_result(result, temp_path)
        return result


def default_on_success(self, retval, task_id, args, kwargs):
    # create thumbnails and set runjob status to HAS_FINISHED after successfully processing an image object.
    result = Result.objects.get(pk=retval)
    result.run_job.status = RunJobStatus.HAS_FINISHED
    result.run_job.save()

    res = create_thumbnails.s(result)
    res.apply_async()


def default_on_failure(self, *args, **kwargs):
    runjob = RunJob.objects.get(pk=args[2][1])  # index into args to fetch the failed runjob instance
    runjob.status = RunJobStatus.FAILED
    runjob.save()
