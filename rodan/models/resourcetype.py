from django.db import models
from uuidfield import UUIDField

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
    mimetype = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    extension = models.CharField(max_length=50, blank=True)

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
    load('image/onebit+png', '', 'png')
    load('image/greyscale+png', '', 'png')
    load('image/grey16+png', '', 'png')
    load('image/rgb+png', '', 'png')
    load('application/mei+xml', '', 'mei')
    load('image/jp2', 'jpeg2000', 'jp2')  # RFC 3745
    load('application/zip', 'Package', 'zip')
    load('application/gamera+xml', 'Gamera classifier XML', 'xml')
    load('application/json', 'JSON', 'json')
    load('text/plain', 'Plain text', 'txt')
