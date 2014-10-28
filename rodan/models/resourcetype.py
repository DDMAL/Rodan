from django.db import models
from uuidfield import UUIDField

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

    _cache = {}
    @staticmethod
    def cached(mime_or_mimelist):
        "return cached object(s) of type names for performance"
        if not isinstance(mime_or_mimelist, list) and not isinstance(mime_or_mimelist, tuple):
            mime = mime_or_mimelist         # not iterable

            if mime in ResourceType._cache:
                return ResourceType._cache[mime]
            else:
                obj = ResourceType.objects.get(mimetype=mime)  # could raise exception models.DoesNotExist
                ResourceType._cache[mime] = obj
                return obj
        else:
            mimelist = mime_or_mimelist     # iterable

            return_objs = []
            for mime in mimelist:
                return_objs.append(ResourceType.cached(mime))
            return return_objs

    _cached_mimetypes = ()
    @staticmethod
    def cached_filter(fn=lambda name: True):
        "Return cached Rodan ResourceTypes according to filter function on mimetype field."
        if not ResourceType._cached_mimetypes:
            ResourceType._cached_mimetypes = tuple(ResourceType.objects.all().values_list('mimetype', flat=True))
        return ResourceType.cached(filter(fn, ResourceType._cached_mimetypes))
