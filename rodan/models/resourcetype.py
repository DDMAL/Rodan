from django.db import models
from uuidfield import UUIDField

_cache = {}

class ResourceType(models.Model):
    """
    A ResourceType is [TODO]
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
    load('image/float+png', '', 'png')
    load('image/complex+png', '', 'png')
    load('application/mei+xml', '', 'mei')
    load('image/jp2', 'jpeg2000', 'jp2')  # RFC 3745
    load('application/zip', 'Package', 'zip')
    load('application/gamera+xml', 'Gamera classifier XML', 'xml')
