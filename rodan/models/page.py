from django.db import models


class Page(models.Model):
    project = models.ForeignKey('rodan.Project')
    page_image = models.FileField(upload_to="images", null=True)
    page_order = models.IntegerField(null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'rodan'

    def __unicode__(self):
        return unicode(self.page_image.name)
