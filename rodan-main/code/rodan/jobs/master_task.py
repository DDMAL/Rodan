from celery import registry, task
from rodan.models import (
    # UserPreference,
    RunJob,
    WorkflowRun,
    Input
)
from rodan.constants import task_status
from django.db.models import Q
from django.conf import settings

import sys
if sys.version_info.major == 2:
    import thread
elif sys.version_info.major == 3:
    import threading as thread
else:
    raise Exception("[-] Python version not supported.")

# Read more on Django queries: https://docs.djangoproject.com/en/dev/topics/db/queries/


@task(name="rodan.core.master_task")
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

    # find and lock runable RunJobs
    # 1. Get a list of Inputs that belong to perhaps runable RunJobs and have their
    #    Resources and/or ResourceLists unsatisfied
    unpromising_inputs = Input.objects.filter(
        Q(run_job__workflow_run__uuid=workflow_run_id)  # its RunJob in the workflow
        & Q(run_job__status=task_status.SCHEDULED)  # its RunJob is SCHEDULED
        & Q(
            run_job__lock__isnull=True
        )  # its RunJob not locked by other concurrent master tasks
        & ~(
            # It has Resource and its Resource is ready.
            (Q(resource__isnull=False) & ~Q(resource__resource_file__exact=""))
            # OR (it should have ResourceList) its ResourceList is not empty and
            # has all Resources ready.
            | (
                Q(resource_list__resources__isnull=False)
                & ~Q(resource_list__resources__resource_file__exact="")
            )
        )
    )
    unpromising_runjob_uuids = unpromising_inputs.values_list(
        "run_job__uuid", flat=True
    ).distinct()
    # 2.
    locked_runjobs_count = RunJob.objects.filter(
        Q(workflow_run__uuid=workflow_run_id)  # RunJob in the workflow
        & Q(status=task_status.SCHEDULED)  # RunJob is SCHEDULED
        & Q(lock__isnull=True)  # RunJob not locked by other concurrent master tasks
        & ~Q(uuid__in=unpromising_runjob_uuids)
    ).update(lock=thread_id)

    if locked_runjobs_count == 0:
        if not RunJob.objects.filter(
            Q(workflow_run__uuid=workflow_run_id) & ~Q(status=task_status.FINISHED)
        ).exists():
            # WorkflowRun has finished!
            WorkflowRun.objects.filter(uuid=workflow_run_id).update(
                status=task_status.FINISHED
            )

            # Send an email to owner of WorkflowRun
            workflowrun = WorkflowRun.objects.get(uuid=workflow_run_id)
            user = WorkflowRun.objects.get(uuid=workflow_run_id).creator
            if not settings.TEST:
                if (
                    user.email
                    and getattr(settings, 'EMAIL_USE', False)
                    and user.user_preference.send_email
                ):
                    subject = "Workflow Run '{0}' FINISHED".format(workflowrun.name)
                    body = "A workflow run you started has finished.\n\n"
                    body = body + "Name: {0}\n".format(workflowrun.name)
                    body = body + "Description: {0}".format(workflowrun.description)
                    to = [user.email]
                    registry.tasks["rodan.core.send_email"].apply_async(
                        (subject, body, to)
                    )

            # return value is ignored, and provided as information in Celery stdout.
            return "wfRun {0} FINISHED".format(workflow_run_id)
        else:
            # return value is ignored, and provided as information in Celery stdout.
            return "wfRun {0} NO RUNABLE RUNJOBS NOW".format(workflow_run_id)
    else:
        runable_runjobs_query = RunJob.objects.filter(lock=thread_id)
        runable_runjobs = list(
            runable_runjobs_query.values("uuid", "job_name", "job_queue")
        )  # immediate evaluation
        runable_runjobs_query.update(
            status=task_status.PROCESSING, lock=None
        )  # unlock now because the task status has been changed

        for rj_value in runable_runjobs:
            task = registry.tasks[str(rj_value["job_name"])]
            queue = str(rj_value["job_queue"])
            runjob_id = str(rj_value["uuid"])
            # task will call master_task synchronously. Don't use Celery's chain,
            # it's hard to revoke.
            async_task = task.si(runjob_id).apply_async(queue=queue)
            RunJob.objects.filter(uuid=runjob_id).update(
                celery_task_id=async_task.task_id
            )

        # return value is ignored, and provided as information in Celery stdout.
        return "wfRun {0} PROCESSING".format(workflow_run_id)
