import os
from django.db import models
from rodan.models.gameraXML import GameraXML


class Classifier(GameraXML):

    @property
    def directory_path(self):
        return os.path.join(self.project.project_path, "classifiers")

    name = models.CharField(max_length=255)
    project = models.ForeignKey("rodan.Project", related_name="classifiers")  # workflows.py does it differently.

    def save(self, *args, **kwargs):
        super(Classifier, self).save(*args, **kwargs)
        if not os.path.exists(self.directory_path):
            os.makedirs(self.directory_path)

    def __unicode__(self):
        return u"classifier" + str(self.uuid)
