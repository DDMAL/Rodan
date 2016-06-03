import mimetypes
import uuid
from django.conf import settings
from django.db import models
from django.db.models.signals import m2m_changed
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from sortedm2m.fields import SortedManyToManyField

import logging
logger = logging.getLogger('rodan')

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
        app_label = 'rodan'
        permissions = (
            ('view_resourcelist', 'View ResourceList'),
        )

    def __unicode__(self):
        return u"<ResourceList {0}>".format(self.uuid)

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey('rodan.Project', blank=True, null=True, db_index=True, on_delete=models.CASCADE)
    resources = SortedManyToManyField('rodan.Resource', blank=True, null=True)
    resource_type = models.ForeignKey('rodan.ResourceType', blank=True, null=True, db_index=True, on_delete=models.PROTECT)
    origin = models.ForeignKey('rodan.Output', related_name="+", null=True, blank=True, on_delete=models.SET_NULL, db_index=True)  # no backward reference

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
