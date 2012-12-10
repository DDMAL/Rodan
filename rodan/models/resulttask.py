from django.db import models
from djcelery.models import TaskMeta


class ResultTask(models.Model):
    result = models.ForeignKey('rodan.Result')
    task = models.ForeignKey(TaskMeta)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'rodan'
