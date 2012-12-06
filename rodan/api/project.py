from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie import fields

from rodan.api.rodanuser import UserResource
from rodan.models.project import Project


class ProjectResource(ModelResource):
    creator = fields.ForeignKey(UserResource, 'creator')

    class Meta:
        queryset = Project.objects.all()
        resource_name = "project"
        authorization = Authorization()
        # Add it here.
        # authentication = BasicAuthentication()
        # authorization = DjangoAuthorization()
        always_return_data = True
