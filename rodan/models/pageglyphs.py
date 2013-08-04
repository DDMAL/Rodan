import os

from django.core.urlresolvers import reverse
from django.db import models

from rodan.models.gameraXML import GameraXML
from rodan.settings import BASE_URL


class PageGlyphs(GameraXML):

    @property
    def directory_path(self):
        return os.path.join(self.classifier.project.project_path, "pageglyphs")

    classifier = models.ForeignKey("rodan.Classifier", related_name="pageglyphs")
    #classifiers = models.ManyToManyField(Classifier, related_name="pageglyphs", blank=False)
    # TODO: this should be many to many when implementing 'Open page glyphs into editor'
    # But I can't figure out how to implement directory_path in that case because I don't have an instance of a classifier to ask for the project path.

    class Meta(GameraXML.Meta):
        verbose_name_plural = "page glyphs"

    def get_absolute_url(self):
        rel_path = reverse('pageglyphs-detail', kwargs={'pk': str(self.uuid)})
        return BASE_URL + rel_path

    def __unicode__(self):
        return u"pageglyphs" + str(self.uuid)
