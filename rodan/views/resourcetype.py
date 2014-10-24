from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from rodan.models import ResourceType
from rodan.serializers.resourcetype import ResourceTypeSerializer

class ResourceTypeList(generics.ListAPIView):
    model = ResourceType
    serializer_class = ResourceTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
    paginate_by = None


class ResourceTypeDetail(generics.RetrieveAPIView):
    model = ResourceType
    serializer_class = ResourceTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
