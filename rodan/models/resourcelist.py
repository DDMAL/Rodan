import uuid
from django.db import models
from sortedm2m.fields import SortedManyToManyField
from django.contrib.auth.models import User
from django.apps import apps

import logging

logger = logging.getLogger("rodan")


class ResourceList(models.Model):
    """
    A `ResourceList` collects a number of `Resource`s in order.

    **Fields**

    - `uuid`
    - `name` -- user-assigned name of this `Resource`.
    - `description` -- description of this `Resource`.
    - `project` -- the reference to `Project` that it belongs to.
    - `resources` -- the references to `Resource`s.
    - `resource_type` -- the reference to required `ResourceType`.
    - `origin` -- the reference to the `Output` by which it was generated.

    - `created`
    - `updated`
    """

    class Meta:
        app_label = "rodan"
        permissions = (("view_resourcelist", "View ResourceList"),)

    def __unicode__(self):
        return u"<ResourceList {0}>".format(self.uuid)

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey(
        "rodan.Project",
        related_name="resourcelists",
        db_index=True,
        on_delete=models.CASCADE,
    )
    resources = SortedManyToManyField("rodan.Resource", blank=True, null=True)
    resource_type = models.ForeignKey(
        "rodan.ResourceType",
        blank=True,
        null=True,
        db_index=True,
        on_delete=models.PROTECT,
    )
    origin = models.ForeignKey(
        "rodan.Output",
        related_name="+",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )  # no backward reference
    creator = models.ForeignKey(
        User,
        related_name="resourcelists",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    @property
    def resource_type(self):
        if self.resources.count() == 0:
            return apps.get_model(
                app_label="rodan", model_name="ResourceType"
            ).objects.get(mimetype="application/octet-stream")
        else:
            return self.resources.first().resource_type
