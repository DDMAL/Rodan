from rest_framework import generics, permissions
import django_filters.rest_framework as filters
from rest_framework.filters import OrderingFilter

from rodan.models.job import Job
from rodan.serializers.job import JobSerializer
from rodan.paginators.pagination import CustomPaginationWithDisablePaginationOption


class JobList(generics.ListAPIView):
    """
    Returns a list of all Jobs. Does not accept POST requests, since
    Jobs should be defined and loaded server-side.
    """

    permission_classes = (permissions.AllowAny,)
    queryset = Job.objects.all().order_by('category', 'name') 
    serializer_class = JobSerializer
    pagination_class = CustomPaginationWithDisablePaginationOption
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter,)
    filter_fields = {
        # "category": map(lambda j:str(j['category']), Job.objects.values('category').distinct()),
        "category": ["exact"],
        "interactive": ["exact"],
        "enabled": ["exact"],
        "uuid": ["exact"],
        "name": ["exact", "icontains"],
    }

    # def get_queryset(self):
    #     filter_dict = {}

    #     if 'workflow_run' in self.request.query_params:
    #         wfrun_id = self.request.query_params['workflow_run']
    #         wf_id = Workflow.objects.filter(
    #             workflow_runs__uuid=wfrun_id).values_list(
    #                 'uuid',
    #                 flat=True
    #         )
    #         filter_dict['workflow_jobs__workflow__uuid__in'] = wf_id

    #     return Job.objects.filter(**filter_dict)


class JobDetail(generics.RetrieveAPIView):
    """
    Query a single Job instance.
    """

    permission_classes = (permissions.AllowAny,)
    queryset = Job.objects.all().order_by('name')
    serializer_class = JobSerializer
    filter_backends = ()
