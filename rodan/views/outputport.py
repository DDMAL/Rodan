from rest_framework import generics
from rest_framework import permissions
from rodan.models.outputport import OutputPort
from rodan.serializers.outputport import OutputPortSerializer


class OutputPortList(generics.ListCreateAPIView):
    model = OutputPort
    serializer_class = OutputPortSerializer
    permission_classes = (permissions.IsAuthenticated, )
    paginate_by = None


class OutputPortDetail(generics.RetrieveUpdateDestroyAPIView):
    model = OutputPort
    serializer_class = OutputPortSerializer
    permission_classes = (permissions.IsAuthenticated, )
