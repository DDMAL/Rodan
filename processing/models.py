import os
from django.db import models
from projects.models import Workflow, Page, Job, RodanUser

import gamera.core as gam
from gamera.plugins import threshold


class Result(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)

    job = models.ForeignKey(Job)
    page = models.ForeignKey(Page)
    rodan_user = models.ForeignKey(RodanUser)

    class Meta:
        unique_together = ("job","page")


class ResultFile(models.Model):
    file_name = models.CharField(max_length=50)
    path_to_file = models.CharField(max_length=200)

    result = models.ForeignKey(Result)


class ActionParameter(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)

    result = models.ForeignKey(Result)




