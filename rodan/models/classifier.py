
from django.db import models
from uuidfield import UUIDField

import os

from rodan.models.gameraXML import GameraXML
from rodan.models.project import Project


class Classifier(models.Model, GameraXML):

    @property
    def directory_path(self):
        return os.path.join(self.project.project_path, "classifiers")

    def upload_path(self, filename):
        return self.file_path

    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, related_name="classifiers")  # workflows.py does it differently.
    classifier_file = models.FileField(upload_to=upload_path, null=True, max_length=255)

    def __unicode__(self):
        return u"classifier" + str(self.uuid)
