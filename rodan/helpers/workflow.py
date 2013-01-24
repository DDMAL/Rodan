import os
from django.core.files import File
from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflow import Workflow
from rodan.models.result import Result
from celery import registry


def run_workflow(workflow_id):
    """
        Does all the magic to turn a Gamera module into
        a Celery task and run it with settings.
    """
    workflow = Workflow.objects.get(pk=workflow_id)
    pages = workflow.pages.all()

    workflow_jobs = WorkflowJob.objects.filter(workflow__uuid=workflow_id).order_by('sequence')
    for page in pages:
        # construct the workflow by creating a task chain for each image.
        # To kick it off we will define a first "Result", which will simply
        # be a copy of the original image saved as a result.

        # create a task chain from the workflow jobs for this image.
        task_chain = []
        for wjob in workflow_jobs:
            rodan_task = registry.tasks[str(wjob.job.name)]
            if wjob.job_settings:
                rodan_task.module_settings = wjob.job_settings

            rodan_task.workflowjob_obj = wjob
            task_chain.append(rodan_task)

        # now we kick it off by passing this result to the first job in the chain
        f = open(os.path.join(page.image_path, "compat_file.png"), 'rb')
        r = Result(
            page=page,
            workflow_job=workflow_jobs[0],
            task_name=workflow_jobs[0].job.name
        )
        r.save()
        r.result.save(os.path.join(page.image_path, "compat_file.png"), File(f))
        job_data = {
            'previous_result': r
        }

        first_task = task_chain[0]
        execute_tasks = [fn.s() for fn in task_chain[1:]]

        res = first_task.s(job_data)
        for t in execute_tasks:
            res.link(t)
        res.apply_async()
