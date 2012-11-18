from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization

from rodan.models.job import Job


class JobResource(ModelResource):
    class Meta:
        queryset = Job.objects.all()
        resource_name = "job"
        # Add it here.
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
