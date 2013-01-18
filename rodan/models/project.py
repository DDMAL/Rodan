from django.db import models
from django.contrib.auth.models import User
from uuidfield import UUIDField


class Project(models.Model):
    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, related_name="projects")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'rodan'

    def __unicode__(self):
        return u"{0}".format(self.name)
