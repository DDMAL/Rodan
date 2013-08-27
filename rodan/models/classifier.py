import os
from django.db import models
from django.contrib.auth.models import User

from rodan.models.gameraXML import GameraXML


class Classifier(GameraXML):

    @property
    def directory_path(self):
        return os.path.join(self.project.project_path, "classifiers")

    name = models.CharField(max_length=255)
    project = models.ForeignKey("rodan.Project", related_name="classifiers")  # workflows.py does it differently.
    creator = models.ForeignKey(User, related_name="classifiers", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    optimal_setting = models.ForeignKey("rodan.ClassifierSetting", related_name="optimal_for",
                                        null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        super(Classifier, self).save(*args, **kwargs)
        if not os.path.exists(self.directory_path):
            os.makedirs(self.directory_path)

    def __unicode__(self):
        return u"classifier" + str(self.uuid)
