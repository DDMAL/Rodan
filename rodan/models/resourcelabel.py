import uuid

from django.contrib.auth.models import User
from django.db import models


class ResourceLabel(models.Model):
    """
    A `Label` is associated with a Rodan Resource.

    **Fields**

    - `name` -- user-assigned name of this `Label`.
    - `uuid` -- unique identifier as a primary key.
    - `creator` -- a reference to the `User`.
    """
    name = models.CharField(max_length=30)
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    # creator = models.ForeignKey(
    #     User,
    #     related_name="label",
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     db_index=True,
    # )

    class Meta:
        app_label = "rodan"
        # permissions = (("view_resource", "View Resource"),)
        ordering = ['name']

    def __str__(self):
        return self.name
