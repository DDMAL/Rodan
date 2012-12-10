from django.db import models


class ResultFile(models.Model):
    class Meta:
        app_label = 'rodan'

    result = models.ForeignKey('rodan.Result')
    result_type = models.CharField(max_length=10)
    filename = models.CharField(max_length=50)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return 'File %s. %s' % (self.filename, self.result)
