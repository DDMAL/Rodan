from rest_framework import generics
from rest_framework import permissions

from rodan.models.result import Result
from rodan.serializers.result import ResultSerializer


class ResultList(generics.ListCreateAPIView):
    model = Result
    paginate_by = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = ResultSerializer

    def get_queryset(self):
        queryset = Result.objects.all()
        workflow_run = self.request.QUERY_PARAMS.get('workflowrun', None)
        page = self.request.QUERY_PARAMS.get('page', None)

        if workflow_run:
            queryset = queryset.filter(run_job__workflow_run__uuid=workflow_run)

        if page:
            queryset = queryset.filter(run_job__page__uuid=page)

        return queryset


class ResultDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Result
    serializer_class = ResultSerializer
