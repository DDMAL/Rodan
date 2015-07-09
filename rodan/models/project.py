import os
import shutil
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from uuidfield import UUIDField
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver


class Project(models.Model):
    """
    The top-level model. A `Project` is mostly administrative and organizational.
    `Resource`s, `Workflow`s belong to `Project`s.

    **Fields**

    - `uuid`
    - `name`
    - `description`
    - `creator` -- a foreign key to the `User` who created the `Project`.
    - `created`
    - `updated`

    **Properties**

    - `project_path` -- the project directory in the filesystem.
    - `workflow_count` -- the count of `Workflow`s under the `Project`.
    - `resource_count` --  the count of `Resource`s under the `Project`.

    **Methods**

    - `save` -- create the project directory if it does not exist.
    - `delete` -- delete the whole project directory.
    """
    @property
    def project_path(self):
        return os.path.join(settings.MEDIA_ROOT, "projects", str(self.uuid))

    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, related_name="projects", blank=True, null=True, on_delete=models.SET_NULL)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<Project {0}>".format(self.name)

    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs)
        if not os.path.exists(self.project_path):
            os.makedirs(self.project_path)

    def delete(self, *args, **kwargs):
        proj_path = self.project_path
        super(Project, self).delete(*args, **kwargs)
        if os.path.exists(proj_path):
            shutil.rmtree(proj_path)

    class Meta:
        app_label = 'rodan'
        ordering = ("created",)
        permissions = (
            ('view_projects', 'Can view projects'),
        )

    @property
    def workflow_count(self):
        return self.workflows.count()

    @property
    def resource_count(self):
        return self.resources.count()

@receiver(post_save, sender=Project)
def notify_socket_subscribers(sender, instance, created, **kwargs):
    from ws4redis.publisher import RedisPublisher
    from ws4redis.redis_store import RedisMessage

    publisher = RedisPublisher(facility='rodan', broadcast=True)
    if created:
        message = RedisMessage("CREATED")
    else:
        message = RedisMessage("UPDATED")
    print('publishing a message')

    publisher.publish_message(message)

