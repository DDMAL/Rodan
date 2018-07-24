from django.db import models
from django.conf import settings
import uuid

import logging

logger = logging.getLogger("rodan")


class ResourceType(models.Model):
    """
    Describes the resource types built in Rodan. Every `ResourceType` is based on
    a standard or custom MIME-type, to help other applications understand Rodan's
    resource types as much as possible.

    **Fields**

    - `uuid`
    - `mimetype` -- a string in MIME-type format. `application/octet-stream` stands
      for unknown type.
    - `description` -- optional string.
    - `extension` -- extension name (after dot) assigned to compatible resource files
      to help the static file server find the best MIME-types.
    """

    class Meta:
        app_label = "rodan"

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    mimetype = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.CharField(max_length=255, blank=True, db_index=True)
    extension = models.CharField(max_length=50, blank=True, db_index=True)

    def __unicode__(self):
        return u"<ResourceType {0}>".format(self.mimetype)

    def delete(self, *args, **kwargs):
        # find all Resource Distributor workflowjobs that have this resourcetype as their setting and set it to default
        from rodan.models import Job, WorkflowJob

        resource_distributor_uuid = Job.objects.get(name="Resource Distributor").uuid
        distributor_wfjs = WorkflowJob.objects.filter(job_id=resource_distributor_uuid)
        for distributor_wfj in distributor_wfjs:
            if distributor_wfj.job_settings["Resource type"] == self.mimetype:
                distributor_wfj.job_settings[
                    "Resource type"
                ] = "application/octet-stream"
                distributor_wfj.save()
        super(ResourceType, self).delete(*args, **kwargs)
