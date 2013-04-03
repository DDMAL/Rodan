import os
import shutil
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from uuidfield import UUIDField


class Project(models.Model):
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

    def delete(self, *args, **kwargs):
        if os.path.exists(self.project_path):
            shutil.rmtree(self.project_path)
        super(Project, self).delete(*args, **kwargs)

    class Meta:
        app_label = 'rodan'
