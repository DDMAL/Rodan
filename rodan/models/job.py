from django.db import models
from django_extensions.db.fields import json


class Job(models.Model):
    name = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)

    input_types = json.JSONField()
    output_types = json.JSONField()
    arguments = json.JSONField(blank=True, null=True)

    is_enabled = models.BooleanField()
    is_automatic = models.BooleanField()
    is_required = models.BooleanField()

    class Meta:
        app_label = 'rodan'
