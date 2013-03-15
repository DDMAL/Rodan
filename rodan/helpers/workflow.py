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

        job_data = {
            'current_wf_job_uuid': workflow_jobs[0].uuid,
        }

        job_chain = []
        for wjob in workflow_jobs:
            rodan_task = registry.tasks[str(wjob.job.name)]
            job_chain.append(rodan_task)

        res = chain([job_chain[0].s(job_data)] + [wjob.s() for wjob in job_chain[1:]])
        res.apply_async()
