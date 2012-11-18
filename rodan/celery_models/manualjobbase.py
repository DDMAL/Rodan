from rodan.models.result import Result
from rodan.celery_models.jobbase import JobBase


class ManualJobBase(JobBase):
    def on_post(self, result_id, **kwargs):
        """
        Start the next automatic job.

        ManualJobBase should be used when there is no celery task required
        (and so there is no need to delay anything).
        """
        result = Result.objects.get(pk=result_id)
        result.page.start_next_automatic_job(result.user)
