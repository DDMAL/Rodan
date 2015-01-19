import os
import mimetypes
import shutil
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from uuidfield import UUIDField
from django.db.models.signals import m2m_changed
from django.core.exceptions import ObjectDoesNotExist
from rodan.constants import task_status

import logging
logger = logging.getLogger('rodan')

def upload_path(resource_obj, filename):
    # user-uploaded file -- keep original extension
    _, ext = os.path.splitext(filename)
    return os.path.join(resource_obj.resource_path, "original_file{0}".format(ext.lower()))

def compat_path(resource_obj, filename):
    # compatible file -- use Rodan extensions
    # We need extension in filesystem as a cue for HTTP server to figure out the best mimetype when user downloads it.
    ext = resource_obj.resource_type.extension
    if ext:
        ext = '.{0}'.format(ext)
    return os.path.join(resource_obj.resource_path, "compat_file{0}".format(ext))

class Resource(models.Model):
    """
    A `Resource` is associated with a Rodan Project.

    **Fields**

    - `uuid`
    - `name` -- user-assigned name of this `Resource`.
    - `project` -- a reference to the `Project`.

    - `resource_file` -- original file uploaded by user. This can be null, if the
      `Resource` was produced by a `RunJob`.
    - `processing_status` -- an integer, indicating the status of conversion of
      user-loaded resource file.
      It can be null if the `Resource` was produced by a `RunJob`.
    - `error_summary` -- a field storing the error summary of conversion process.
    - `error_details` -- a field storing the error details of conversion process.
    - `creator` -- a reference to the `User` if it is user-uploaded.

    - `compat_resource_file` -- Rodan-compatible resource file. It can be produced
      by a `RunJob`, or converted from user-uploaded file.
    - `resource_type` -- a reference to the `ResourceType`. `application/octet-stream`
      stands for arbitrary type.

    - `origin` -- a reference to the `Output` model associated with the `RunJob`
      that produced the `Resource`. This can be null, if the `Resource` was uploaded
      by user, and not produced as an output file of a `RunJob`.
    - `created`
    - `updated`

    - `has_thumb` -- denote whether it has thumbnails

    **Properties**

    - `resource_path` -- local path of resource folder.
    - `resource_file_path` -- local path of user-uploaded resource file. Return None
      if user-uploaded file does not exist.
    - `resource_url` -- exposed URL of user-uploaded resource file. Return None
      if user-uploaded file does not exist.
    - `filename` -- filename of user-uploaded resource file.
    - `compat_file_url` -- exposed URL of compatible resource file. Return None
      if compatible resource file does not exist.
    - `thumb_path` -- local path of thumbnail folder.
    - `thumb_url` -- exposed URL of thumbnail folder.
    - `small_thumb_url` -- exposed URL of small thumbnail.
    - `medium_thumb_url` -- exposed URL of middle thumbnail.
    - `large_thumb_url` -- exposed URL of large thumbnail.

    **Methods**

    - `__init__` -- keep an original copy of resource type. If the user changes the type,
      detecting the change does not need to hit the database again.
    - `save` -- create local paths of resource folder and thumbnail folder. Invalidate
      all associated `Workflow`s when resource type is manually changed.
    - `delete` -- delete local paths of resource folder and thumbnail folder. Invalidate
      all associated `Workflow`s.
    """

    def __init__(self, *a, **k):
        super(Resource, self).__init__(*a, **k)
        self.___original_resource_type = self.resource_type  # keep an original copy

    class Meta:
        app_label = 'rodan'

    STATUS_CHOICES = [(task_status.SCHEDULED, "Scheduled"),
                      (task_status.PROCESSING, "Processing"),
                      (task_status.FINISHED, "Finished"),
                      (task_status.FAILED, "Failed"),
                      (task_status.NOT_APPLICABLE, "Not applicable")]

    @property
    def resource_path(self):
        return os.path.join(self.project.project_path, "resources", str(self.uuid))

    def __unicode__(self):
        return u"<Resource {0}>".format(self.uuid)

    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    project = models.ForeignKey('rodan.Project', related_name="resources")
    resource_file = models.FileField(upload_to=upload_path, max_length=255, blank=True)
    compat_resource_file = models.FileField(upload_to=compat_path, max_length=255, blank=True)
    resource_type = models.ForeignKey('rodan.ResourceType', related_name='resources')

    processing_status = models.IntegerField(choices=STATUS_CHOICES, blank=True, null=True)
    error_summary = models.TextField(default="")
    error_details = models.TextField(default="")

    creator = models.ForeignKey(User, related_name="resources", null=True, blank=True)
    origin = models.ForeignKey('rodan.Output', related_name="+", null=True, blank=True)  # no backward reference

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    has_thumb = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(Resource, self).save(*args, **kwargs)
        if not os.path.exists(self.resource_path):
            os.makedirs(self.resource_path)

        if not os.path.exists(self.thumb_path):
            os.makedirs(self.thumb_path)

        if self.resource_type != self.___original_resource_type:
            for ra in self.resource_assignments.all():
                wf = ra.input_port.workflow_job.workflow
                wf.valid = False
                wf.save()
            for rc in self.resource_collections.all():
                wf = rc.workflow
                wf.valid = False
                wf.save()

    def delete(self, *args, **kwargs):
        if os.path.exists(self.resource_path):
            shutil.rmtree(self.resource_path)
        for ra in self.resource_assignments.all():
            wf = ra.input_port.workflow_job.workflow
            wf.valid = False
            wf.save()
        for rc in self.resource_collections.all():
            wf = rc.workflow
            wf.valid = False
            wf.save()
        super(Resource, self).delete(*args, **kwargs)

    @property
    def resource_file_path(self):
        if self.resource_file:
            return os.path.dirname(self.resource_file.path)

    @property
    def thumb_path(self):
        return os.path.join(self.resource_path, "thumbnails")

    @property
    def thumb_url(self):
        return os.path.join(settings.MEDIA_URL, os.path.relpath(self.resource_path, settings.MEDIA_ROOT), "thumbnails")

    @property
    def resource_url(self):
        if self.resource_file:
            return os.path.join(settings.MEDIA_URL, os.path.relpath(self.resource_file.path, settings.MEDIA_ROOT))

    @property
    def compat_file_url(self):
        if self.compat_resource_file:
            return os.path.join(settings.MEDIA_URL, os.path.relpath(self.compat_resource_file.path, settings.MEDIA_ROOT))

    def thumb_filename(self, size):
        return "{0}.{1}".format(size, settings.THUMBNAIL_EXT)

    @property
    def filename(self):
        if self.resource_file:
            return os.path.basename(self.resource_file.path)

    @property
    def small_thumb_url(self):
        if self.has_thumb:
            return os.path.join(self.thumb_url,
                                self.thumb_filename(size=settings.SMALL_THUMBNAIL))

    @property
    def medium_thumb_url(self):
        if self.has_thumb:
            return os.path.join(self.thumb_url,
                                self.thumb_filename(size=settings.MEDIUM_THUMBNAIL))

    @property
    def large_thumb_url(self):
        if self.has_thumb:
            return os.path.join(self.thumb_url,
                                self.thumb_filename(size=settings.LARGE_THUMBNAIL))
