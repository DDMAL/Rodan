from rest_framework import generics
from rest_framework import permissions
from rodan.models.outputporttype import OutputPortType
from rodan.serializers.outputporttype import OutputPortTypeSerializer


class OutputPortTypeList(generics.ListCreateAPIView):
    model = OutputPortType
    serializer_class = OutputPortTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
    paginate_by = None


class OutputPortTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    model = OutputPortType
    serializer_class = OutputPortTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
