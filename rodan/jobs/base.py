from celery import Task
from rodan.models.runjob import RunJob, RunJobStatus

class RodanJob(Task):

    def run_task(self, result_id, runjob_id, *args, **kwargs):
        """
        This is where all the execution code of a job goes.
        """
        pass

    def run(self, result_id, runjob_id, *args, **kwargs):
        runjob = RunJob.objects.get(pk=runjob_id)
        if runjob.status != RunJobStatus.CANCELLED:
            return self.run_task(result_id, runjob_id, *args, **kwargs)
