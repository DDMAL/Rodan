from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie import fields

from django.contrib.auth.models import User
from rodan.models.rodanuser import RodanUser


class RodanUserResource(ModelResource):
    class Meta:
        queryset = RodanUser.objects.all()
        resource_name = "rodanuser"
        include_resource_uri = False
        include_absolute_url = False


class UserResource(ModelResource):
    profile = fields.ToOneField(RodanUserResource, 'get_profile', full=True)

    class Meta:
        queryset = User.objects.all()
        resource_name = "user"
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
