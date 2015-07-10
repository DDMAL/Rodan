import os
from django.db import models
from uuidfield import UUIDField
from rodan.constants import task_status
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

class WorkflowRun(models.Model):
    """
    Represents the running of a workflow. Since Rodan is based on a RESTful design,
    `Workflow`s are *not* run by sending a command like "run workflow". Rather,
    they are run by creating a new `WorkflowRun` instance.

    **Fields**

    - `uuid`
    - `project` -- a reference to the `Project`.
    - `workflow` -- a reference to the `Workflow`. If the `Workflow` is deleted, this
      field will be set to None.
    - `creator` -- a reference to the `User`.
    - `status` -- indicating the status of the `WorkflowRun`.

    - `name` -- user's name to the `WorkflowRun`.
    - `description` -- user's description of the `WorkflowRun`.

    - `created`
    - `updated`

    **Properties**

    - `origin_resources` -- a list of origin `Resource` UUIDs.
    """
    STATUS_CHOICES = [(task_status.PROCESSING, "Processing"),
                      (task_status.FINISHED, "Finished"),
                      (task_status.FAILED, "Failed"),
                      (task_status.CANCELLED, "Cancelled"),
                      (task_status.RETRYING, "Retrying")]

    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    project = models.ForeignKey('rodan.Project', related_name="workflow_runs", on_delete=models.CASCADE)
    workflow = models.ForeignKey('rodan.Workflow', related_name="workflow_runs", blank=True, null=True, on_delete=models.SET_NULL)
    creator = models.ForeignKey('auth.User', related_name="workflow_runs", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.IntegerField(choices=STATUS_CHOICES, default=task_status.PROCESSING)

    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def origin_resources(self):
        return list(set(self.run_jobs.values_list('resource_uuid', flat=True)))

    def __unicode__(self):
        return u"<WorkflowRun {0}>".format(str(self.uuid))

@receiver(post_save, sender=WorkflowRun)
def notify_socket_subscribers(sender, instance, created, **kwargs):
    from ws4redis.publisher import RedisPublisher
    from ws4redis.redis_store import RedisMessage

    publisher = RedisPublisher(facility='rodan', broadcast=True)
    if created:
        message = RedisMessage("CREATED workflowrun")
    else:
        message = RedisMessage("UPDATED workflowrun")
    print('publishing a message')

    publisher.publish_message(message)
