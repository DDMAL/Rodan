from celery import registry, task
from rodan.models import RunJob, Resource, WorkflowRun
from rodan.constants import task_status
from django.db.models import Q
import thread

# Read more on Django queries: https://docs.djangoproject.com/en/dev/topics/db/queries/

@task(name='rodan.core.master_task')
def master_task(workflow_run_id):
    """
    Core task for Rodan job assignments.

    Code here are run asynchronously in Celery thread.

    To prevent re-creating a deleted object, any write to database should use
    one of the following:
    + `queryset.update()`
    + `obj.save(update_fields=[...])`
    + `obj.file_field.save(..., save=False)` + `obj.save(update_fields=['file_field'])`

    instead of:
    + `obj.save()`
    + `obj.file_field.save(..., save=True)`
    """
    thread_id = str(thread.get_ident())

    # find and lock runable runjobs
    locked_runjobs_count = RunJob.objects.filter(
        Q(workflow_run__uuid=workflow_run_id)
        & Q(status=task_status.SCHEDULED)
        & (~Q(inputs__resource__compat_resource_file__exact='')   # not having ANY input with compat_resource_file==''
           | Q(inputs__isnull=True))      # OR no input
        & Q(lock__isnull=True)    # not locked by other concurrent master tasks
    ).update(lock=thread_id)

    if locked_runjobs_count == 0:
        if not RunJob.objects.filter(Q(workflow_run__uuid=workflow_run_id) & ~Q(status=task_status.FINISHED)).exists():
            # WorkflowRun has finished!
            WorkflowRun.objects.filter(uuid=workflow_run_id).update(status=task_status.FINISHED)
            return "wfRun FINISHED"
        else:
            return "wfRun NO RUNABLE RUNJOBS NOW"
    else:
        runable_runjobs_query = RunJob.objects.filter(lock=thread_id)
        runable_runjobs = list(runable_runjobs_query.values('uuid', 'job_name'))  # immediate evaluation
        runable_runjobs_query.update(status=task_status.PROCESSING, lock=None)  # unlock now because the task status has been changed

        for rj_value in runable_runjobs:
            task = registry.tasks[str(rj_value['job_name'])]
            runjob_id = str(rj_value['uuid'])
            async_task = (task.si(runjob_id) | master_task.si(workflow_run_id)).apply_async()
            RunJob.objects.filter(uuid=runjob_id).update(celery_task_id=async_task.task_id)

        return "wfRun PROCESSING"
