import os
from django.core.files import File
from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflow import Workflow
from rodan.models.result import Result
from celery import registry, chain


def run_workflow(workflow_id):
    """
        Does all the magic to turn a Gamera module into
        a Celery task and run it with settings.
    """
    workflow = Workflow.objects.get(pk=workflow_id)
    pages = workflow.pages.filter(processed=True)  # only get images that are ready to be processed

    for page in pages:
        workflow_jobs = WorkflowJob.objects.filter(workflow__uuid=workflow_id, page=page).order_by('sequence')
        # construct the workflow by creating a task chain for each image.
        # To kick it off we will define a first "Result", which will simply
        # be a copy of the original image saved as a result.
        # now we kick it off by passing this result to the first job in the chain
        f = open(os.path.join(page.image_path, "compat_file.png"), 'rb')
        r = Result(
            workflow_job=workflow_jobs[0],
            task_name="rodan.initial.copy_task"
        )
        r.save()
        r.result.save(os.path.join(page.image_path, "compat_file.png"), File(f))

        job_data = {
            'previous_result': r
        }

        job_chain = []
        for wjob in workflow_jobs:
            rodan_task = registry.tasks[str(wjob.job.name)]
            job_chain.append(rodan_task)

        res = chain([job_chain[0].s(job_data)] + [wjob.s() for wjob in job_chain[1:]])
        res.apply_async()
