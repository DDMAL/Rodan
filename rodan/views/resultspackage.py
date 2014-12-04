from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from celery import registry
from celery.task.control import revoke
from django.core.urlresolvers import resolve, Resolver404

from rodan.serializers.resultspackage import ResultsPackageSerializer, ResultsPackageListSerializer
from rodan.models import ResultsPackage
from rodan.constants import task_status
from rodan.jobs.helpers import package_results


class ResultsPackageList(generics.ListCreateAPIView):
    model = ResultsPackage
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ResultsPackageListSerializer
    queryset = ResultsPackage.objects.all()  # [TODO] filter for current user?
    filter_fields = ('creator', 'workflow_run')

    def perform_create(self, serializer):
        # check status
        rp = serializer.save(creator=self.request.user) # expiry_date
        rp_id = str(rp.uuid)

        package_task = registry.tasks[str(package_results.name)]
        package_task.apply_async((rp_id, True)) # TODO


class ResultsPackageDetail(generics.RetrieveAPIView):
    model = ResultsPackage
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ResultsPackageSerializer
    queryset = ResultsPackage.objects.all()  # [TODO] filter for current user?
