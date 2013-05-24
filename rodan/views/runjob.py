from rest_framework import generics
from rest_framework import permissions

from rodan.models.runjob import RunJob
from rodan.models.runjob import RunJobStatus
from rodan.serializers.runjob import RunJobSerializer


class RunJobList(generics.ListAPIView):
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
    paginate_by = None

    def get_queryset(self):
        requiresInteraction = self.request.QUERY_PARAMS.get('requires_interaction', 0)
        queryset = RunJob.objects.all()
        if requiresInteraction:
            queryset = queryset.filter(needs_input=1).filter(status__in=[RunJobStatus.WAITING_FOR_INPUT, RunJobStatus.RUN_ONCE_WAITING])
        return queryset


class RunJobDetail(generics.RetrieveUpdateAPIView):
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
