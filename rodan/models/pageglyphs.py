import os

from django.db import models
from uuidfield import UUIDField

from rodan.models.gameraXML import GameraXML
from rodan.models.classifier import Classifier


class PageGlyphs(models.Model, GameraXML):
    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255)
    classifier = models.ManyToManyField(Classifier, related_name="pageglyphs", blank=True)  # TODO: should be many to many
        # setting blank True:  Although the classifier will be set by the job settings and page glyphs will always have a classifier,
        # I'll leave blank true anyway because we don't need to enforce pageGlyphs to always have a classifier that way.
        # (Conceptually, page glyphs CAN exist without a classifier.)

    def __unicode__(self):
        return u"pageglyphs" + str(self.uuid)

    @property
    def directory_path(self):
        return os.path.join(self.classifier.project.project_path, "pageglyphs")

    # Thoughts about PageGlyph model...
    # Associate to Project?  Or to WFRun?  Or to Manual Job?  Or to Classifier?  I think we said classifier.
    # That could make sense... if they chose a classifier when they set up the job.
    # The job certainly makes page glyphs.  Maybe the classifier interface (only) allows the choice of the classifier.
    # Well, both would be ideal.  You can choose a classifier when you make the (manual) job... and if you don't and you hit work on job, you just wouldn't have a classifier at all.
    # No... you NEED a classifier before you can work on page glyphs, so let's constrain that you choose a classifier for the manual job.  You type in the name and if it's not
    # created, it makes it for you.
    # (Note that in the automatic job, you always a classifier in the settings.)
    # Ok, so in the manual classifier job, you choose a classifier.
