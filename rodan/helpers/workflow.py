from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflow import Workflow
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

        for workflow_job in workflow_jobs:
            workflow_job.workflow_run = workflow.last_run
            workflow_job.save()

        job_data = {
            'current_wf_job_uuid': workflow_jobs[0].uuid,
        }

        job_chain = []
        for wjob in workflow_jobs:
            rodan_task = registry.tasks[str(wjob.job.name)]
            job_chain.append(rodan_task)

        res = chain([job_chain[0].s(job_data)] + [wjob.s() for wjob in job_chain[1:]])
        res.apply_async()

    # update the last run variable
    workflow.last_run += 1
    workflow.save()


def test_workflow(workflow_id, page_id):
    """
        Similar to run workflow, but only operating on a single page, and doesn't increment the run count.
    """
    workflow = Workflow.objects.get(pk=workflow_id)

    # new_run = workflow.run + 1
    page = workflow.pages.filter(processed=True, pk=page_id)  # only get images that are ready to be processed
    workflow_jobs = WorkflowJob.objects.filter(workflow__uuid=workflow_id).order_by('sequence')

    for workflow_job in workflow_jobs:
        workflow_job.page = page[0]
        # workflow_job.workflow_run = new_run
        workflow_job.save()

    job_data = {
        'current_wf_job_uuid': workflow_jobs[0].uuid,
    }

    job_chain = []
    for wjob in workflow_jobs:
        rodan_task = registry.tasks[str(wjob.job.job_name)]
        job_chain.append(rodan_task)

    res = chain([job_chain[0].s(job_data)] + [wjob.s() for wjob in job_chain[1:]])
    res.apply_async()


def clean_test_workflow(workflow_id):
    pass
