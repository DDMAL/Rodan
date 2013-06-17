
from django.db import models
from uuidfield import UUIDField

import os

from rodan.models.gameraXML import GameraXML
from rodan.models.classifier import Classifier


class PageGlyphs(models.Model, GameraXML):
    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255)
    classifier = models.ForeignKey(Classifier, related_name="pageglyphs")
    #classifiers = models.ManyToManyField(Classifier, related_name="pageglyphs", blank=False)
    # TODO: this should be many to many when implementing 'Open page glyphs into editor'
    # But I can't figure out how to implement directory_path in that case because I don't have an instance of a classifier to ask for the project path.

    class Meta:
        app_label = 'rodan'
        verbose_name_plural = "page glyphs"

    def __unicode__(self):
        return u"pageglyphs" + str(self.uuid)

    @property
    def directory_path(self):
        return os.path.join(self.classifier.project.project_path, "pageglyphs")
