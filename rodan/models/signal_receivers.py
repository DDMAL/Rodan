from django.db.models.signals import post_save
from django.dispatch import receiver

from rodan.models.workflow import Workflow
from rodan.models.page import Page
from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflowrun import WorkflowRun


@receiver(post_save, sender=WorkflowRun)
def update_workflow_upon_workflow_run_update(**kwargs):
    workflowrun_instance = kwargs['instance']
    workflow_instance = workflowrun_instance.workflow
    super(Workflow, workflow_instance).save()  # touch the workflow to update the updated field.


@receiver(post_save, sender=Page)
def update_workflow_upon_page_save(**kwargs):
    print "Hey"
    page_instance = kwargs['instance']
    workflows = page_instance.workflows.all()
    for workflow_instance in workflows:
        super(Workflow, workflow_instance).save()


@receiver(post_save, sender=WorkflowJob)
def update_workflow_upon_workflowjob_save(**kwargs):
    workflowjob_instance = kwargs['instance']
    workflow_instance = workflowjob_instance.workflow
    super(Workflow, workflow_instance).save()
