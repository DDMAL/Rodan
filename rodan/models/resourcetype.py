from django.db import models
from uuidfield import UUIDField

class ResourceType(models.Model):
    """
    A ResourceType is [TODO]
    """
    class Meta:
        app_label = 'rodan'

    mimetype = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=255, blank=True)

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
