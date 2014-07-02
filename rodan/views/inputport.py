from rest_framework import generics
from rodan.models.inputport import InputPort
from rodan.serializers.inputport import InputPortSerializer


class InputPortList(generics.ListCreateAPIView):
    model = InputPort
    serializer_class = InputPortSerializer


class InputPortDetail(generics.RetrieveUpdateDestroyAPIView):
    model = InputPort
    serializer_class = InputPortSerializer
