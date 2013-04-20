from rest_framework import generics
from rest_framework import permissions

from rodan.models.runjob import RunJob
from rodan.serializers.runjob import RunJobSerializer


class RunJobList(generics.ListAPIView):
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
    paginate_by = None


class RunJobDetail(generics.RetrieveUpdateAPIView):
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
