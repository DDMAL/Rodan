from celery import registry, task
from rodan.models import RunJob, Resource
from rodan.models.runjob import RunJobStatus

@task(name='rodan.jobs.RodanMaster.rodan_master')
def rodan_master(workflow_run_id):
    # code here are run asynchronously. Any write to database should use `queryset.update()` method, instead of `obj.save()`.

    # preconfigure interactive runjobs and set them ready for input
    interactive_runjobs = RunJob.objects.filter(workflow_run__uuid=workflow_run_id,
                          status=RunJobStatus.NOT_RUNNING,
                          inputs__resource__compat_resource_file__gt='',  # http://stackoverflow.com/questions/4771464/django-queryset-filter-for-blank-filefield
                          needs_input=True,
                          ready_for_input=False
    )
    i_runjob_values = interactive_runjobs.values('uuid', 'workflow_job__job__job_name')
    for i_runjob_value in i_runjob_values:
        task = registry.tasks[str(i_runjob_value['workflow_job__job__job_name'])]
        runjob_id = str(i_runjob_value['uuid'])
        task.preconfigure(runjob_id)
    interactive_runjobs.update(ready_for_input=True)


    # find runable runjobs
    runable_runjobs = RunJob.objects.filter(
        workflow_run__uuid=workflow_run_id,
        status=RunJobStatus.NOT_RUNNING,
        inputs__resource__compat_resource_file__gt='',  # http://stackoverflow.com/questions/4771464/django-queryset-filter-for-blank-filefield
        needs_input=False
    ).values('uuid', 'workflow_job__job__job_name')

    if len(runable_runjobs) == 0:
        return False
    else:
        for rj_value in runable_runjobs:
            task = registry.tasks[str(rj_value['workflow_job__job__job_name'])]
            runjob_id = str(rj_value['uuid'])
            runjob_query = RunJob.objects.filter(uuid=rj_value['uuid'])

            runjob_query.update(status=RunJobStatus.RUNNING)  # in test, tasks are executed synchronously, therefore update the status before dispatching the task
            async_task = (task.s(runjob_id) | rodan_master.si(workflow_run_id)).apply_async()
            runjob_query.update(celery_task_id=async_task.task_id)
        return True
