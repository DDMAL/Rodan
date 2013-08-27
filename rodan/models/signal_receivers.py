from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from rodan.models.workflow import Workflow
from rodan.models.page import Page
from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflowrun import WorkflowRun
from rodan.models.runjob import RunJob, RunJobStatus
from rodan.models.classifiersetting import ClassifierSetting


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


@receiver(post_save, sender=ClassifierSetting)
def update_optimal_setting_upon_classifiersetting_save(**kwargs):
    new_setting = kwargs['instance']
    producer = new_setting.producer
    if producer is None or new_setting.fitness is None:
        return None

    related_settings = producer.classifier_settings.order_by('-fitness')
    if not related_settings.exists():
        new_optimal = new_setting
    else:
        previous_optimal = related_settings[0]
        new_optimal = max(new_setting, previous_optimal, key=lambda x: x.fitness)

    producer.optimal_setting = new_optimal
    producer.save()


## The following two signal receivers fix the issue of workflowjob sequence numbers,
## but I believe this issue is best handled on the client. Although the code below
## have been tested and if seems like it works, saving other workflowjobs in a
## workflowjob signal handler will induce several maintenance nightmares.

# @receiver(pre_save, sender=WorkflowJob)
# def fix_job_sequence_after_removing_workflowjob_from_workflow(**kwargs):
#     workflowjob_instance = kwargs['instance']
#     if workflowjob_instance.workflow is not None:
#         return

#     db_workflowjob = WorkflowJob.objects.get(pk=str(workflowjob_instance.uuid))
#     if db_workflowjob.workflow is None:
#         return

#     wfjob_list = db_workflowjob.workflow.workflow_jobs.order_by('sequence')

#     deleted_sequence_number = workflowjob_instance.sequence
#     wfjobs_with_wrong_sequence = wfjob_list[deleted_sequence_number:]

#     for j, wfjob in enumerate(wfjobs_with_wrong_sequence, start=deleted_sequence_number):
#         wfjob.sequence = j
#         wfjob.save()


# @receiver(pre_save, sender=WorkflowJob)
# def fix_job_sequence_when_insering_workflowjob_in_the_middle_of_workflow(**kwargs):
#     workflowjob_instance = kwargs['instance']

#     if (workflowjob_instance.pk is not None
#         or workflowjob_instance.sequence is None
#         or workflowjob_instance.workflow is None):
#         return

#     wfjob_list = workflowjob_instance.workflow.workflow_jobs.order_by('sequence')
#     print wfjob_list
#     print len(wfjob_list)
#     print workflowjob_instance.sequence

#     if workflowjob_instance.sequence == len(wfjob_list) + 1:
#         return

#     wfjobs_with_wrong_sequence = wfjob_list[workflowjob_instance.sequence - 1:]

#     print wfjobs_with_wrong_sequence

#     for i, wfjob in enumerate(wfjobs_with_wrong_sequence, start=workflowjob_instance.sequence + 1):
#         wfjob.sequence = i
#         wfjob.save()
