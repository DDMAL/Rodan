from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization

from rodan.models.workflow import Workflow


class WorkflowResource(ModelResource):
    class Meta:
        queryset = Workflow.objects.all()
        resource_name = "workflow"
        # Add it here.
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
