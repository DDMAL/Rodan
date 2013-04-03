from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflow import Workflow
from rodan.models.workflowrun import WorkflowRun
from rodan.models.runjob import RunJob
from rodan.models.page import Page
from celery import registry, chain


def run_workflow(workflow_id, testing=False, page_id=None):
    workflow = Workflow.objects.get(pk=workflow_id)
    if not testing:
        run_num = workflow.runs + 1

    workflow_jobs = WorkflowJob.objects.filter(workflow__uuid=workflow_id).order_by('sequence')

    if not page_id:
        pages = workflow.pages.filter(processed=True)
    else:
        pages = Page.objects.filter(pk=page_id)  # this returns an array of one page to test

    # create a new workflow run
    workflow_run = WorkflowRun(workflow=workflow, run=run_num)
    workflow_run.save()

    return_objects = []
    # this is the workflow.
    for page in pages:
        workflow_chain = []
        for workflow_job in workflow_jobs:
            is_interactive = False if workflow_job.job_type == 0 else True
            runjob = RunJob(workflow_run=workflow_run,
                            workflow_job=workflow_job,
                            job_settings=workflow_job.job_settings,  # copy the most recent settings from the workflow job (these may be modified if the job is interactive)
                            needs_input=is_interactive,      # by default this is set to be True if the job is interactive
                            page=page)
            runjob.save()

            rodan_task = registry.tasks[str(workflow_job.job_name)]
            workflow_chain.append((rodan_task, str(runjob.uuid)))
        first_job = workflow_chain[0]
        res = chain([first_job[0].si(None, first_job[1])] + [job[0].s(job[1]) for job in workflow_chain[1:]])
        res.apply_async()
        return_objects.append(res)

    # finally, update the run_num with the most recent run
    if not testing:
        workflow.runs = run_num
        workflow.save()

    return return_objects
