import os
from celery import task
from django.core.files import File
from rodan.models.result import Result
from rodan.models.runjob import RunJob


@task(ignore_result=True, name="rodan.jobs.devel.dummy_job")
def dummy_job(result_id, runjob_id, *args, **kwargs):
    runjob = RunJob.objects.get(pk=runjob_id)

    if result_id is None:
        page = runjob.page.compat_file_path
    else:
        result = Result.objects.get(result_id)
        page = result.result.path

    new_result = Result(run_job=runjob)
    new_result.save()

    result_save_path = new_result.result_path

    f = open(page, 'rb')
    new_result.result.save(os.path.join(result_save_path, page), File(f))
    f.close()

    return str(new_result.uuid)
