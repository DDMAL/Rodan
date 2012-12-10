from django.db import models


class ActionParam(models.Model):
    """
    Specifies the intended defaults for a job.
    """
    class Meta:
        app_label = 'rodan'
        unique_together = ('job_item', 'key')

    job_item = models.ForeignKey('rodan.JobItem')
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)

    def __unicode__(self):
        return "%s: %s, for %s" % (self.key, self.value, self.job_item)
