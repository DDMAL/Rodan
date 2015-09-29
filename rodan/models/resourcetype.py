from django.db import models
from uuidfield import UUIDField
from django.conf import settings
import os
import yaml

import logging
logger = logging.getLogger('rodan')

_cache = {}

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

    **Class Methods**

    - `ResourceType.load` -- initialize a `ResourceType` if not in database, and
      add it into local `ResourceType` cache.
    - `ResourceType.cached` -- retrieve a cached `ResourceType` instance by MIME-type.
    - `ResourceType.cached_list` -- retrieve a list of cached `ResourceType` instances
      by MIME-type.
    - `ResourceType.all_mimetypes` -- retrieve all MIME-types supported by Rodan.
    """
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    mimetype = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.CharField(max_length=255, blank=True, db_index=True)
    extension = models.CharField(max_length=50, blank=True, db_index=True)

    def __unicode__(self):
        return u"<ResourceType {0}>".format(self.mimetype)

    @staticmethod
    def load(mimetype, description='', extension=''):
        if not ResourceType.objects.filter(mimetype=mimetype).exists():
            rt_obj = ResourceType(mimetype=mimetype, description=description, extension=extension)
            rt_obj.save()
        else:
            rt_obj = ResourceType.objects.get(mimetype=mimetype)

        _cache[mimetype] = rt_obj

    @staticmethod
    def cached(mime):
        return _cache[mime]

    @staticmethod
    def cached_list(mimelist):
        "return cached objects of mimetypes"
        return map(lambda mime: _cache[mime], mimelist)

    @staticmethod
    def all_mimetypes():
        "return all mimetypes in the cache"
        return _cache.keys()


def load_predefined_resource_types():
    load = ResourceType.load  # short-hand
    load('application/octet-stream', 'Unknown type', '')  # RFC 2046
    load('application/zip', 'Package', 'zip')
    load('application/json', 'JSON', 'json')
    load('text/plain', 'Plain text', 'txt')

    # load types from registered job packages
    base_path = os.path.dirname(settings.PROJECT_PATH)

    for package_name in settings.RODAN_JOB_PACKAGES:
        rel_path = os.sep.join(package_name.split('.'))
        resource_type_path = os.path.join(base_path, rel_path, 'resource_types.yaml')
        if os.path.isfile(resource_type_path):
            logger.info("searching " + resource_type_path + " for custom MIME resource types")
            with open(resource_type_path, 'r') as f:
                resource_types = yaml.load(f)
                for rt in resource_types:
                    load(rt['mimetype'], rt.get('description', ''), rt.get('extension', ''))
                    logger.info("resource type " + rt['mimetype'] + " loaded")
