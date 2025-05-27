import uuid

from django.db import models


class ResourceLabel(models.Model):
    """
    A `Label` is associated with a Rodan Resource.

    **Fields**

    - `name` -- user-assigned name of this `Label`.
    - `uuid` -- unique identifier as a primary key.
    """
    name = models.CharField(max_length=36, unique=True)
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    class Meta:
        app_label = "rodan"
        # permissions = (("view_resource", "View Resource"),)
        ordering = ["name"]

    def __str__(self):
        return self.name
