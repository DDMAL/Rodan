from rest_framework import generics
from rodan.models.inputporttype import InputPortType
from rodan.serializers.inputporttype import InputPortTypeSerializer


class InputPortTypeList(generics.ListCreateAPIView):
    model = InputPortType
    serializer_class = InputPortTypeSerializer


class InputPortTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    model = InputPortType
    serializer_class = InputPortTypeSerializer
