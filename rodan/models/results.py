from django.db import models
from rodan.models.projects import JobItem, RodanUser, Page
from rodan.models.jobs import JobType


class Result(models.Model):
    class Meta:
        app_label = 'rodan'
        unique_together = ('job_item', 'page')

    job_item = models.ForeignKey(JobItem)
    user = models.ForeignKey(RodanUser)
    page = models.ForeignKey(Page)
    start_time = models.DateTimeField(auto_now_add=True)
    end_manual_time = models.DateTimeField(null=True)
    end_total_time = models.DateTimeField(null=True)

    def __unicode__(self):
        status = 'Incomplete' if self.end_total_time is None else 'Complete'
        return 'Result of %s on workflow %s - %s' % (self.job_item.job, self.page, status)

    def save_parameters(self, **params):
        for key, value in params.iteritems():
            param = Parameter(result=self, key=key, value=value)
            param.save()

    def create_file(self, filename, result_type=JobType.IMAGE):
        resfile = ResultFile(result=self, filename=filename, result_type=result_type)
        resfile.save()


class Parameter(models.Model):
    class Meta:
        app_label = 'rodan'

    result = models.ForeignKey(Result)
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)

    def __unicode__(self):
        return '%s: %s. %s' % (self.key, self.value, self.result)


class ResultFile(models.Model):
    class Meta:
        app_label = 'rodan'

    result = models.ForeignKey(Result)
    result_type = models.IntegerField()
    filename = models.CharField(max_length=50)

    def __unicode__(self):
        return 'File %s. %s' % (self.filename, self.result)
