from django.db import models
from django.utils import timezone
from django.conf import settings


class Result(models.Model):
    class Meta:
        app_label = 'rodan'
        unique_together = ('job_item', 'page')

    job_item = models.ForeignKey('rodan.JobItem')
    user = models.ForeignKey('rodan.RodanUser')
    page = models.ForeignKey('rodan.Page')
    task_state = models.CharField(max_length=10, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_manual_time = models.DateTimeField(null=True)
    end_total_time = models.DateTimeField(null=True)

    def __unicode__(self):
        status = 'Incomplete' if self.end_total_time is None else 'Complete'
        return 'Result of %s on workflow %s - %s' % (self.job_item.job, self.page, status)

    def get_time_in_queue(self):
        return int((timezone.now() - (self.end_manual_time or self.start_time)).total_seconds())

    def save_parameters(self, **params):
        Parameter = models.get_model('rodan', 'Parameter')
        for key, value in params.iteritems():
            param = Parameter(result=self, key=key, value=value)
            param.save()

    def create_file(self, filename, result_type):
        # Strip the MEDIA_ROOT part from the filename
        len_prefix = len(settings.MEDIA_ROOT)
        ResultFile = models.get_model('rodan', 'ResultFile')
        ResultFile.objects.create(result=self, filename=filename[len_prefix:], result_type=result_type)

    def update_end_manual_time(self):
        self.end_manual_time = timezone.now()
        self.save()

    def update_end_total_time(self):
        self.end_total_time = timezone.now()
        self.save()
