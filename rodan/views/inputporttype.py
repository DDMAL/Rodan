from rest_framework import generics
from rest_framework import permissions
from rodan.models.inputporttype import InputPortType
from rodan.serializers.inputporttype import InputPortTypeSerializer


class InputPortTypeList(generics.ListCreateAPIView):
    model = InputPortType
    serializer_class = InputPortTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
    paginate_by = None


class InputPortTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    model = InputPortType
    serializer_class = InputPortTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
