from django.db import models
from django.utils import timezone
from django.conf import settings

from rodan.models.projects import JobItem, RodanUser, Page
from rodan.models.jobs import JobType

from djcelery.models import TaskState


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

    def get_time_in_queue(self):
        return timezone.now() - (self.end_manual_time or self.start_time)

    def save_parameters(self, **params):
        for key, value in params.iteritems():
            param = Parameter(result=self, key=key, value=value)
            param.save()

    def create_file(self, filename, result_type):
        # Strip the MEDIA_ROOT part from the filename
        len_prefix = len(settings.MEDIA_ROOT)
        ResultFile.objects.create(result=self, filename=filename[len_prefix:], result_type=result_type)

    def update_end_manual_time(self):
        self.end_manual_time = timezone.now()
        self.save()

    def update_end_total_time(self):
        self.end_total_time = timezone.now()
        self.save()


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
    result_type = models.CharField(max_length=10)
    filename = models.CharField(max_length=50)

    def __unicode__(self):
        return 'File %s. %s' % (self.filename, self.result)

class ResultTask(models.Model):
    class Meta:
        app_label = 'rodan'
    result = models.ForeignKey(Result)
    task = models.ForeignKey(TaskState)

