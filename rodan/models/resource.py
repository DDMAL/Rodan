import os
import mimetypes
import uuid
import shutil
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from rodan.constants import task_status

import logging
logger = logging.getLogger('rodan')


def upload_path(resource_obj, filename):
    # user-uploaded file -- keep original extension
    _, ext = os.path.splitext(filename)
    return os.path.join(resource_obj.resource_path, "original_file{0}".format(ext.lower()))


class Resource(models.Model):
    """
    A `Resource` is associated with a Rodan Project.

    **Fields**

    - `uuid`
    - `name` -- user-assigned name of this `Resource`.
    - `description` -- description of this `Resource`.
    - `project` -- a reference to the `Project`.

    - `resource_file` -- original file uploaded by user. This can be null, if the
      `Resource` was produced by a `RunJob`.
    - `processing_status` -- an integer, indicating the status of conversion of
      user-loaded resource file.
      It can be null if the `Resource` was produced by a `RunJob`.
    - `error_summary` -- a field storing the error summary of conversion process.
    - `error_details` -- a field storing the error details of conversion process.
    - `creator` -- a reference to the `User` if it is user-uploaded.

    - `resource_type` -- a reference to the `ResourceType`. `application/octet-stream`
      stands for arbitrary type.

    - `origin` -- a reference to the `Output` model associated with the `RunJob`
      that produced the `Resource`. This can be null, if the `Resource` was uploaded
      by user, and not produced as an output file of a `RunJob`.
    - `created`
    - `updated`

    **Properties**

    - `resource_path` -- local path of resource folder.
    - `resource_file_path` -- local path of user-uploaded resource file. Return None
      if user-uploaded file does not exist.
    - `resource_url` -- exposed URL of user-uploaded resource file. Return None
      if user-uploaded file does not exist.
    - `filename` -- filename of user-uploaded resource file.

    - `diva_path` -- local path of diva data folder.
    - `diva_jp2_path` -- local path of diva JPEG2000 file.
    - `diva_json_path` -- local path of diva JSON measurement file.
    - `diva_image_dir` -- the relative path to IIP server FILESYSTEM_PREFIX, exposed
      to the client.
    - `diva_json_url` -- exposed URL of JSON measurement file.

    - `viewer_relurl` -- exposed URL of resource viewer.

    **Methods**

    - `__init__` -- keep an original copy of resource type. If the user changes the type,
      detecting the change does not need to hit the database again.
    - `save` -- create local paths of resource folder.
    - `delete` -- delete local paths of resource folder.
    """

    class Meta:
        app_label = 'rodan'
        permissions = (
            ('view_resource', 'View Resource'),
        )

    STATUS_CHOICES = [(task_status.SCHEDULED, "Scheduled"),
                      (task_status.PROCESSING, "Processing"),
                      (task_status.FINISHED, "Finished"),
                      (task_status.FAILED, "Failed"),
                      (task_status.NOT_APPLICABLE, "Not applicable")]

    @property
    def resource_path(self):
        return os.path.join(self.project.project_path, "resources", self.uuid.hex)  # backward compability (not using hyphenated UUID)

    def __unicode__(self):
        return u"<Resource {0}>".format(self.uuid)

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey('rodan.Project', related_name="resources", on_delete=models.CASCADE, db_index=True)
    resource_file = models.FileField(upload_to=upload_path, max_length=255, blank=True)
    #compat_resource_file = models.FileField(upload_to=compat_path, max_length=255, blank=True)
    resource_type = models.ForeignKey('rodan.ResourceType', related_name='resources', on_delete=models.PROTECT, db_index=True)

    processing_status = models.IntegerField(choices=STATUS_CHOICES, blank=True, null=True, db_index=True)
    error_summary = models.TextField(default="")
    error_details = models.TextField(default="")

    creator = models.ForeignKey(User, related_name="resources", null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
    origin = models.ForeignKey('rodan.Output', related_name="+", null=True, blank=True, on_delete=models.SET_NULL, db_index=True)  # no backward reference

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    def save(self, *args, **kwargs):
        super(Resource, self).save(*args, **kwargs)
        if not os.path.exists(self.resource_path):
            os.makedirs(self.resource_path)

        # if not os.path.exists(self.thumb_path):
        #     os.makedirs(self.thumb_path)
        #
        # if getattr(settings, 'ENABLE_DIVA') and not os.path.exists(self.diva_path):
        #     os.makedirs(self.diva_path)

    def delete(self, *args, **kwargs):
        if os.path.exists(self.resource_path):
            shutil.rmtree(self.resource_path)
        super(Resource, self).delete(*args, **kwargs)

    @property
    def resource_file_path(self):
        if self.resource_file:
            return os.path.dirname(self.resource_file.path)

    # @property
    # def thumb_path(self):
    #     return os.path.join(self.resource_path, "thumbnails")

    # @property
    # def thumb_url(self):
    #     return os.path.join(settings.MEDIA_URL, os.path.relpath(self.resource_path, settings.MEDIA_ROOT), "thumbnails")

    @property
    def resource_url(self):
        if self.resource_file:
            return os.path.join(settings.MEDIA_URL, os.path.relpath(self.resource_file.path, settings.MEDIA_ROOT))

    # @property
    # def compat_file_url(self):
    #     if self.compat_resource_file:
    #         return os.path.join(settings.MEDIA_URL, os.path.relpath(self.compat_resource_file.path, settings.MEDIA_ROOT))

    # def thumb_filename(self, size):
    #     return "{0}.{1}".format(size, settings.THUMBNAIL_EXT)

    @property
    def filename(self):
        if self.resource_file:
            return os.path.basename(self.resource_file.path)

    # @property
    # def small_thumb_url(self):
    #     if self.has_thumb:
    #         if not settings.ENABLE_DIVA:
    #             return os.path.join(self.thumb_url,
    #                                 self.thumb_filename(size=settings.SMALL_THUMBNAIL))
    #         else:
    #             return "{0}&WID={1}&HEI={1}&CVT={2}".format(self.diva_image_url, settings.SMALL_THUMBNAIL, settings.THUMBNAIL_EXT)
    #
    # @property
    # def medium_thumb_url(self):
    #     if self.has_thumb:
    #         if not settings.ENABLE_DIVA:
    #             return os.path.join(self.thumb_url,
    #                                 self.thumb_filename(size=settings.MEDIUM_THUMBNAIL))
    #         else:
    #             return "{0}&WID={1}&HEI={1}&CVT={2}".format(self.diva_image_url, settings.MEDIUM_THUMBNAIL, settings.THUMBNAIL_EXT)
    #
    # @property
    # def large_thumb_url(self):
    #     if self.has_thumb:
    #         if not settings.ENABLE_DIVA:
    #             return os.path.join(self.thumb_url,
    #                                 self.thumb_filename(size=settings.LARGE_THUMBNAIL))
    #         else:
    #             return "{0}&WID={1}&HEI={1}&CVT={2}".format(self.diva_image_url, settings.LARGE_THUMBNAIL, settings.THUMBNAIL_EXT)


    @property
    def diva_path(self):
        return os.path.join(self.resource_path, "diva")

    @property
    def diva_jp2_path(self):
        return os.path.join(self.diva_path, "image.jp2")

    @property
    def diva_json_path(self):
        return os.path.join(self.diva_path, "measurement.json")

    @property
    def diva_image_dir(self):
        return os.path.relpath(self.diva_path, getattr(settings, 'IIPSRV_FILESYSTEM_PREFIX', '/'))

    @property
    def diva_image_url(self):
        return "{0}?FIF={1}/image.jp2".format(settings.IIPSRV_URL, self.diva_image_dir)

    @property
    def diva_json_url(self):
        return os.path.join(settings.MEDIA_URL, os.path.relpath(self.diva_json_path, settings.MEDIA_ROOT))

    def get_viewer(self):
        if self.resource_type.mimetype.startswith('image') and settings.ENABLE_DIVA:
            return 'diva'
        elif self.resource_type.mimetype.startswith("application/mei+xml"):
            return 'neon'
        else:
            return None

    @property
    def viewer_relurl(self):
        if self.get_viewer() is not None:
            return reverse('resource-viewer-acquire', args=(self.uuid, ))
