import os
import shutil
from django.db import models
from uuidfield import UUIDField
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

class Workflow(models.Model):
    """
    A `Workflow` is a container of jobs and their connections.

    **Fields**

    - `uuid`
    - `name`
    - `description`
    - `project` -- a reference to `Project` where it resides.
    - `creator` -- a reference to `User` who created it.
    - `valid` -- a boolean, indicating whether the contents of `Workflow` is valid.
    - `created`
    - `updated`
    """

    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=100)
    project = models.ForeignKey("rodan.Project", related_name="workflows", on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey("auth.User", related_name="workflows", null=True, blank=True, on_delete=models.SET_NULL)
    valid = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<Workflow {0}>".format(self.name)

    class Meta:
        app_label = 'rodan'
        ordering = ('created',)

@receiver(post_save, sender=Workflow)
def notify_socket_subscribers(sender, instance, created, **kwargs):
    from ws4redis.publisher import RedisPublisher
    from ws4redis.redis_store import RedisMessage

    publisher = RedisPublisher(facility='rodan', broadcast=True)
    if created:
        message = RedisMessage("CREATED workflow")
    else:
        message = RedisMessage("UPDATED workflow")
    print('publishing a message')

    publisher.publish_message(message)
