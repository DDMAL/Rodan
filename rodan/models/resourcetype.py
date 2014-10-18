from django.db import models
from uuidfield import UUIDField

class ResourceType(models.Model):
    """
        A ResourceType is [TODO]
    """

    class Meta:
        app_label = 'rodan'

    name = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=255, blank=True)

    _cache = {}
    @staticmethod
    def list(*args):
        "return a list of cached objects of type names for m2m saving"
        return_objs = []
        for name in args:
            if name in ResourceType._cache:
                return_objs.append(ResourceType._cache[name])
            else:
                obj = ResourceType.objects.get(name=name)  # could raise exception models.DoesNotExist
                ResourceType._cache[name] = obj
                return_objs.append(obj)
        return return_objs
