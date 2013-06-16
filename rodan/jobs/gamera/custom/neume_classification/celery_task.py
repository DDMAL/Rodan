from celery import Task
from rodan.models.runjob import RunJob
from rodan.models.runjob import RunJobStatus
from rodan.models.result import Result
from rodan.helpers.thumbnails import create_thumbnails

JOB_NAME_MANUAL = 'gamera.custom.neume_classification.manual_classification'


class ManualClassificationTask(Task):
    max_retries = None
    name = JOB_NAME_MANUAL

    def run(self, result_id, runjob_id, *args, **kwargs):
        runjob = RunJob.objects.get(pk=runjob_id)
        runjob.status = RunJobStatus.RUNNING
        runjob.save()

        if runjob.needs_input:
            runjob.status = RunJobStatus.WAITING_FOR_INPUT
            runjob.save()
            self.retry(args=[result_id, runjob_id], *args, countdown=10, **kwargs)

        runjob.status = RunJobStatus.RUNNING
        runjob.save()

        print "The job received input."

    def on_success(self, retval, task_id, args, kwargs):
        # create thumbnails and set runjob status to HAS_FINISHED after successfully processing an image object.
        result = Result.objects.get(pk=retval)
        result.run_job.status = RunJobStatus.HAS_FINISHED
        result.run_job.save()

        res = create_thumbnails.s(result)
        res.apply_async()

    def on_failure(self, *args, **kwargs):
        runjob = RunJob.objects.get(pk=args[2][1])  # index into args to fetch the failed runjob instance
        runjob.status = RunJobStatus.FAILED
        runjob.save()
