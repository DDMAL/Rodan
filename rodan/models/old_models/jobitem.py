from django.db import models


class JobItem(models.Model):
    class Meta:
        app_label = 'rodan'
        unique_together = ('workflow', 'sequence')
        ordering = ['sequence']

    workflow = models.ForeignKey('rodan.Workflow')
    job = models.ForeignKey('rodan.Job')
    sequence = models.IntegerField()

    def __unicode__(self):
        return "%s in workflow '%s' (step %d)" % (self.job, self.workflow, self.sequence)
