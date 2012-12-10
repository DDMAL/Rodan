from django.db import models


class Job(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    module = models.CharField(max_length=255)
    enabled = models.CharField(max_length=255)
    is_automatic = models.BooleanField()
    is_required = models.BooleanField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'rodan'
