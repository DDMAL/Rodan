import os
from django.db import models
from uuidfield import UUIDField
from django.conf import settings


class ResultsPackageStatus(object):
    SCHEDULED_FOR_PROCESSING = 0
    PROCESSING = 1
    COMPLETE = 2
    FAILED = -1
    EXPIRED = 8
    CANCELLED = 9


class ResultsPackage(models.Model):
    """
        A ResultsPackage contains a packaged files containing a subset of the results
        produced by a WorkflowRun. It contains the download link to that file. A
        ResultsPackage can be "ordered", and while it's being created, it shows its
        progress in the status field.
    """

    STATUS_CHOICES = [(ResultsPackageStatus.SCHEDULED_FOR_PROCESSING, "Scheduled for processing"),
                      (ResultsPackageStatus.PROCESSING, "Processing"),
                      (ResultsPackageStatus.COMPLETE, "Complete"),
                      (ResultsPackageStatus.EXPIRED, "Expired"),
                      (ResultsPackageStatus.FAILED, "Failed, ZOMG"),
                      (ResultsPackageStatus.CANCELLED, "Cancelled")]

    uuid = UUIDField(primary_key=True, auto=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    percent_completed = models.IntegerField(default=0)
    download_url = models.URLField(blank=True, default='', max_length=255)

    workflow_run = models.ForeignKey("rodan.WorkflowRun", related_name="results_packages")
    pages = models.ManyToManyField("rodan.Page", related_name="results_packages", blank=True)
    jobs = models.ManyToManyField("rodan.Job", related_name="results_packages", blank=True)
    creator = models.ForeignKey("auth.User", related_name="results_packages")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    expiry_date = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return u"<ResultsPackage {0}>".format(str(self.uuid))

    def save(self, *args, **kwargs):
        super(ResultsPackage, self).save(*args, **kwargs)
        if not os.path.exists(self.package_path):
            os.makedirs(self.package_path)

    class Meta:
        app_label = 'rodan'

    @property
    def package_path(self):
        return os.path.join(settings.MEDIA_ROOT, 'results_packages', str(self.uuid))

    @property
    def bag_name(self):
        date_string = self.created.strftime("%Y_%m_%d_%I%M%p")
        return "{0}__{1}".format(self.workflow_run.workflow.name, date_string)

    @property
    def bag_path(self):
        return os.path.join(self.package_path, self.bag_name)

    @property
    def bag_url(self):
        return os.path.join(settings.MEDIA_URL, os.path.relpath(self.bag_path, settings.MEDIA_ROOT))

    @property
    def file_path(self, package_extension='zip'):
        return '.'.join((str(self.bag_path), package_extension))

    @property
    def file_url(self):
        return os.path.join(settings.MEDIA_URL, os.path.relpath(self.file_path, settings.MEDIA_ROOT))
