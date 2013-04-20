from rest_framework import generics
from rodan.models.job import Job
from rodan.serializers.job import JobSerializer


class JobList(generics.ListAPIView):
    model = Job
    serializer_class = JobSerializer
    paginate_by = None

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        enabled = self.request.QUERY_PARAMS.get('enabled', None)
        queryset = Job.objects.all()
        if enabled:
            queryset = queryset.filter(enabled=enabled)
        return queryset


class JobDetail(generics.RetrieveAPIView):
    model = Job
    serializer_class = JobSerializer
