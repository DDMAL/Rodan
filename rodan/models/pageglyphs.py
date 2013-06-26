import os
from uuidfield import UUIDField

from django.db import models
from django.core.urlresolvers import reverse

from rodan.models.gameraXML import GameraXML
from rodan.models.classifier import Classifier
from rodan.settings import BASE_URL


class PageGlyphs(models.Model, GameraXML):

    @property
    def directory_path(self):
        return os.path.join(self.classifier.project.project_path, "pageglyphs")

    def upload_path(self, filename):
        return self.file_path

    uuid = UUIDField(primary_key=True, auto=True)
    classifier = models.ForeignKey(Classifier, related_name="pageglyphs")
    #classifiers = models.ManyToManyField(Classifier, related_name="pageglyphs", blank=False)
    # TODO: this should be many to many when implementing 'Open page glyphs into editor'
    # But I can't figure out how to implement directory_path in that case because I don't have an instance of a classifier to ask for the project path.
    pageglyphs_file = models.FileField(upload_to=upload_path, null=True, max_length=255)

    class Meta:
        app_label = 'rodan'
        verbose_name_plural = "page glyphs"

    def get_absolute_url(self):
        rel_path = reverse('pageglyphs-detail', kwargs={'pk': str(self.uuid)})
        return BASE_URL + rel_path

    def __unicode__(self):
        return u"pageglyphs" + str(self.uuid)
