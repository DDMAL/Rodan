from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from rodan.models.workflow import Workflow
from rodan.models.page import Page
from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflowrun import WorkflowRun
from rodan.models.runjob import RunJob, RunJobStatus


@receiver(post_save, sender=WorkflowRun)
def update_workflow_upon_workflow_run_update(**kwargs):
    workflowrun_instance = kwargs['instance']
    workflow_instance = workflowrun_instance.workflow
    super(Workflow, workflow_instance).save()  # touch the workflow to update the updated field.


@receiver(post_save, sender=Page)
def update_workflow_upon_page_save(**kwargs):
    page_instance = kwargs['instance']
    workflows = page_instance.workflows.all()
    for workflow_instance in workflows:
        super(Workflow, workflow_instance).save()


@receiver(pre_save, sender=RunJob)
def clear_runjob_error_fields(**kwargs):
    # If runjob status is not 'FAILED', we clear the error messages.
    runjob_instance = kwargs['instance']
    if runjob_instance.status != RunJobStatus.FAILED:
        runjob_instance.error_summary = ''
        runjob_instance.error_details = ''


@receiver(post_save, sender=WorkflowJob)
def update_workflow_upon_workflowjob_save(**kwargs):
    workflowjob_instance = kwargs['instance']
    if workflowjob_instance.workflow:
        workflow_instance = workflowjob_instance.workflow
        super(Workflow, workflow_instance).save()


@receiver(pre_save, sender=WorkflowJob)
def update_workflow_upon_workflowjob_removal(**kwargs):
    workflowjob_instance = kwargs['instance']
    if workflowjob_instance.workflow is None:
        db_workflowjob = WorkflowJob.objects.get(pk=str(workflowjob_instance.uuid))
        if db_workflowjob.workflow:
            workflow_instance = db_workflowjob.workflow
            super(Workflow, workflow_instance).save()
