from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization

from rodan.models.project import Project


class ProjectResource(ModelResource):
    class Meta:
        queryset = Project.objects.all()
        resource_name = "project"
        # Add it here.
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
