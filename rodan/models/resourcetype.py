from django.db import models
from django.conf import settings
import uuid

import logging
logger = logging.getLogger('rodan')

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
        app_label = 'rodan'

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    mimetype = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.CharField(max_length=255, blank=True, db_index=True)
    extension = models.CharField(max_length=50, blank=True, db_index=True)

    def __unicode__(self):
        return u"<ResourceType {0}>".format(self.mimetype)
