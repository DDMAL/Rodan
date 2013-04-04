from rest_framework import generics
from rest_framework import permissions

from rodan.models.runjob import RunJob
from rodan.serializers.runjob import RunJobSerializer


class RunJobList(generics.ListCreateAPIView):
    model = RunJob
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = RunJobSerializer


class RunJobDetail(generics.RetrieveUpdateDestroyAPIView):
    model = RunJob
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = RunJobSerializer
