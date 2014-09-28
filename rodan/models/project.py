import os
import shutil
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from uuidfield import UUIDField
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class Project(models.Model):
    """
        A Project is mostly administrative and organizational. It's the top-level model.

        Pages, Workflows, and Classifiers belong to a project.
    """
    @property
    def project_path(self):
        return os.path.join(settings.MEDIA_ROOT, "projects", str(self.uuid))

    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, related_name="projects")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<Project {0}>".format(self.name)

    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs)
        if not os.path.exists(self.project_path):
            os.makedirs(self.project_path)

    class Meta:
        app_label = 'rodan'
        ordering = ("created",)
        permissions = (
            ('view_projects', 'Can view projects'),
        )

    @property
    def workflow_count(self):
        return self.workflows.count()


@receiver(pre_delete)
def delete_project_dir(sender, instance, **kwargs):
    """
    Overridden model methods are not called on bulk operations. Must use signal.
    https://docs.djangoproject.com/en/1.7/topics/db/models/#overriding-model-methods
    """
    if sender is Project:
        if os.path.exists(instance.project_path):
            shutil.rmtree(instance.project_path)
