
from django.db import models
from uuidfield import UUIDField

import os

from rodan.models.gameraXML import GameraXML
from rodan.models.project import Project


class Classifier(models.Model, GameraXML):
    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, related_name="classifiers")  # workflows.py does it differently.

    def __unicode__(self):
        return u"classifier" + str(self.uuid)

    @property
    def directory_path(self):
        return os.path.join(self.project.project_path, "classifiers")
