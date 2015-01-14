import os, datetime
from django.db import models
from uuidfield import UUIDField
from django.conf import settings
from rodan.constants import task_status


class ResultsPackage(models.Model):
    """
    A `ResultsPackage` contains a packaged files containing the produced results of a
    subset of `Output`s in a `WorkflowRun`.

    **Fields**

    - `uuid`
    - `status` -- an integer indicating the status of `ResultsPackage`.
    - `percent_completed` -- an integer indicating the progress of packaging.
    - `workflow_run` -- the reference to `WorkflowRun`.
    - `packaging_mode` -- the packaging mode of the `ResultsPackage`, leading to different
      directory structure and contents inside the package.
    - `creator`
    - `celery_task_id` -- the corresponding Celery task.
    - `error_summary` -- summary of error when packaging fails.
    - `error_details` -- details of error when packaging fails.
    - `created`
    - `expiry_time`

    **Properties**

    - `package_path` -- the local path of the package.
    - `package_relurl` -- the relative URL of the package.

    **Methods**

    - `delete` -- delete the package in the filesystem.
    """
    DEFAULT_EXPIRY_TIME = datetime.timedelta(days=30)

    STATUS_CHOICES = [(task_status.SCHEDULED, "Scheduled"),
                      (task_status.PROCESSING, "Processing"),
                      (task_status.FINISHED, "Finished"),
                      (task_status.FAILED, "Failed"),
                      (task_status.CANCELLED, "Cancelled"),
                      (task_status.EXPIRED, "Expired")]

    PACKAGING_MODE_CHOICES = [(0, "Only endpoint resources"),
                              (1, "All resources -- subdirectoried by resource names"),
                              (2, "Diagnosis, including all inputs/outputs/settings -- subdirectoried by workflow job and resource names")]

    uuid = UUIDField(primary_key=True, auto=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=task_status.SCHEDULED)
    percent_completed = models.IntegerField(default=0)

    workflow_run = models.ForeignKey("rodan.WorkflowRun", related_name="results_packages")
    packaging_mode = models.IntegerField(choices=PACKAGING_MODE_CHOICES)
    creator = models.ForeignKey("auth.User", related_name="results_packages")
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)

    error_summary = models.TextField(default="", blank=True, null=True)
    error_details = models.TextField(default="", blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField(blank=True, null=True)

    def delete(self, *a, **k):
        path = self.package_path
        if os.path.isfile(path):
            os.remove(path)
        super(ResultsPackage, self).delete(*a, **k)

    def __unicode__(self):
        return u"<ResultsPackage {0}>".format(str(self.uuid))

    class Meta:
        app_label = 'rodan'

    @property
    def package_path(self):
        return get_package_path(self.uuid)

    @property
    def package_relurl(self):
        return "{0}/{1}".format(settings.MEDIA_URL, get_package_relpath(self.uuid))

def get_package_relpath(rp_uuid):
    return 'results_packages/{0}.zip'.format(rp_uuid)
def get_package_path(rp_uuid):
    return os.path.join(settings.MEDIA_ROOT, get_package_relpath(rp_uuid))
