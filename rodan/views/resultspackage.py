import urlparse
import warnings

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from django.core.urlresolvers import resolve, Resolver404
from django.contrib.auth.models import User

from rodan.models.job import Job
from rodan.models.workflowrun import WorkflowRun
from rodan.models.page import Page
from rodan.serializers.resultspackage import ResultsPackageSerializer, ResultsPackageListSerializer
from rodan.models.resultspackage import ResultsPackage, ResultsPackageStatus
from rodan.helpers.resultspackagemanager import PackageResultTask


class ResultsPackageList(generics.ListCreateAPIView):
    model = ResultsPackage
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ResultsPackageListSerializer
    paginate_by = None

    def _resolve_object(self, object_class, object_url, error_dict={'400': [], '404': []}):
        url_path = urlparse.urlparse(object_url).path
        try:
            object_view = resolve(url_path)
            print object_view
        except Resolver404:
            error_dict['400'] += [str(object_url)]
        else:
            try:
                db_object = object_class.objects.get(pk=object_view.kwargs['pk'])
            except object_class.DoesNotExist:
                error_dict['404'] += [str(object_url)]
            else:
                return db_object.pk

    def get_queryset(self):
        queryset = ResultsPackage.objects.all()

        creator_url = self.request.QUERY_PARAMS.get('creator', None)
        if creator_url:
            creator_instance = self._resolve_object(User, creator_url)
            if creator_instance:  # Checking if creator could be successfully resolved. Silently ignore filter otherwise.
                queryset = queryset.filter(creator=creator_instance)
            else:
                print "Filtering by creator failed. Something wrong with the url {0}".format(creator_url)

        workflow_run_url = self.request.QUERY_PARAMS.get('workflowrun', None)
        if workflow_run_url:
            workflowrun_instance = self._resolve_object(WorkflowRun, workflow_run_url)
            if workflowrun_instance:
                queryset = queryset.filter(workflow_run=workflowrun_instance)
            else:
                print "Filtering by workflow_run failed. Something wrong with the url {0}.".format(workflow_run_url)

        return queryset

    def post(self, request, *args, **kwargs):
        workflow_run_url = request.DATA.get('workflow_run_url', None)
        page_urls = request.DATA.get('page_urls', None)
        job_urls = request.DATA.get('job_urls', None)

        if not workflow_run_url:
            return Response({"message": "You must specify a workflow_run ID"}, status=status.HTTP_400_BAD_REQUEST)

        url_path = urlparse.urlparse(workflow_run_url).path
        try:
            workflow_run_view = resolve(url_path)
        except Resolver404:
            return Response({"message": "Invalid workflow_run url"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            workflowrun = WorkflowRun.objects.get(pk=workflow_run_view.kwargs['pk'])
        except WorkflowRun.DoesNotExist:
            return Response({"message": "You must specify an existing workflow"}, status=status.HTTP_404_NOT_FOUND)

        if page_urls:
            page_errors = {'400': [], '404': []}
            pages = [self._resolve_object(Page, page_url, page_errors) for page_url in page_urls]

            if page_errors['400']:
                return Response({"message": "One or more pages have invalid url.",
                                 "bad_urls:": page_errors['400']},
                                status=status.HTTP_400_BAD_REQUEST)
            if page_errors['404']:
                return Response({"message": "One or more pages could not be located.",
                                 "bad_urls": page_errors['404']},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            pages = []

        if job_urls:
            job_errors = {'400': [], '404': []}
            jobs = [self._resolve_object(Job, job_url, job_errors) for job_url in job_urls]
            if job_errors['400']:
                return Response({"message": "One or more jobs have invalid url.",
                                 "bad_urls": job_errors['400']},
                                status=status.HTTP_400_BAD_REQUEST)
            if job_errors['404']:
                return Response({"message": "One or more jobs could not be located.",
                                 "bad_urls": job_errors['404']},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            jobs = []

        package = ResultsPackage.objects.create(workflow_run=workflowrun, creator=request.user,
                                                expiry_date=None)  # Will change this. Can't figure out how to work with timezone support right now.

        package.pages.add(*pages)
        package.jobs.add(*jobs)

        package.status = ResultsPackageStatus.SCHEDULED_FOR_PROCESSING
        package.save()
        async_task = PackageResultTask()
        async_task.delay(str(package.uuid))

        return Response(ResultsPackageSerializer(package, context={'request': request}).data)


class ResultsPackageDetail(generics.RetrieveAPIView):
    model = ResultsPackage
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ResultsPackageSerializer
