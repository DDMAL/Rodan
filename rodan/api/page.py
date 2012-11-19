from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie import fields

from rodan.api.project import ProjectResource
from rodan.api.workflow import WorkflowResource
from rodan.models.page import Page


class PageResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')
    workflow = fields.ForeignKey(WorkflowResource, 'workflow')

    class Meta:
        queryset = Page.objects.all()
        resource_name = "page"
        # Add it here.
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
