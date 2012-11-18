from django.db import models
from djcelery.models import TaskMeta


class ResultTask(models.Model):
    class Meta:
        app_label = 'rodan'
    result = models.ForeignKey('rodan.Result')
    task = models.ForeignKey(TaskMeta)
