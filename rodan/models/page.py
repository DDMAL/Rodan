from django.db import models
from rodan.models.project import Project


class Page(models.Model):
    project = models.ForeignKey(Project, related_name="pages")
    page_image = models.FileField(upload_to="images", null=True)
    page_order = models.IntegerField(null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'rodan'

    def __unicode__(self):
        return unicode(self.page_image.name)
