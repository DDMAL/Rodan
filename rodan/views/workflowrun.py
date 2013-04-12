import urlparse
import celery
from django.core.urlresolvers import resolve

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from rodan.models.workflow import Workflow
from rodan.models.page import Page
from rodan.models.runjob import RunJob
from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflowrun import WorkflowRun
from rodan.serializers.workflowrun import WorkflowRunSerializer


class WorkflowRunList(generics.ListCreateAPIView):
    model = WorkflowRun
    permission_classes = (permissions.AllowAny, )
    serializer_class = WorkflowRunSerializer

    def get_queryset(self):
        workflow = self.request.QUERY_PARAMS.get('workflow', None)
        run = self.request.QUERY_PARAMS.get('run', None)

        queryset = WorkflowRun.objects.all()
        if workflow:
            queryset = queryset.filter(workflow__uuid=workflow)
        if run:
            queryset = queryset.filter(run=run)

        return queryset

    def post(self, request, *args, **kwargs):
        """
            In the Rodan RESTful architecture, "running" a workflow is accomplished by creating a new
            WorkflowRun object.
        """
        # workflow = request.QUERY_PARAMS.get('workflow', None)
        workflow = request.DATA.get('workflow', None)
        test_status = request.QUERY_PARAMS.get('test', None)
        page_id = request.QUERY_PARAMS.get('page_id', None)

        if not workflow:
            return Response({"message": "You must specify a workflow ID"}, status=status.HTTP_400_BAD_REQUEST)

        value = urlparse.urlparse(workflow).path
        try:
            w = resolve(value)
        except:
            return Response({"message": "Could not resolve ID to workflow object"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            workflow_obj = Workflow.objects.get(pk=w.kwargs.get('pk'))
        except:
            return Response({"message": "You must specify an existing workflow"}, status=status.HTTP_404_NOT_FOUND)

        workflow_jobs = WorkflowJob.objects.filter(workflow=workflow_obj).order_by('sequence')

        if not workflow_jobs.exists():
            return Response({"message": "No jobs for workflow {0} were specified".format(workflow)}, status=status.HTTP_400_BAD_REQUEST)

        if test_status:
            # running in test mode. This runs the workflow on a single page.
            if not page_id:
                return Response({"message": "You must specify a page ID if you are running in test mode."}, status=status.HTTP_400_BAD_REQUEST)

            pages = Page.objects.filter(pk=page_id)
            run_num = None
            test_status = True

            if not pages.exists():
                return Response({"message": "No pages for page ID {0} were found".format(page_id)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            pages = workflow_obj.pages.filter(processed=True)
            run_num = workflow_obj.runs + 1
            test_status = False

            if not pages:
                return Response({"message": "No pages were assigned to workflow ID {0}".format(workflow)}, status=status.HTTP_400_BAD_REQUEST)

        workflow_run = WorkflowRun(workflow=workflow_obj, run=run_num, test_run=test_status)

        workflow_run.save()

        return_objects = []
        for page in pages:
            workflow_chain = []
            for workflow_job in workflow_jobs:
                is_interactive = False if workflow_job.job_type == 0 else True
                runjob = RunJob(workflow_run=workflow_run,
                                workflow_job=workflow_job,
                                job_settings=workflow_job.job_settings,  # copy the most recent settings from the workflow job (these may be modified if the job is interactive)
                                needs_input=is_interactive,      # by default this is set to be True if the job is interactive
                                page=page)
                runjob.save()

                rodan_task = celery.registry.tasks[str(workflow_job.job_name)]
                workflow_chain.append((rodan_task, str(runjob.uuid)))
            first_job = workflow_chain[0]
            res = celery.chain([first_job[0].si(None, first_job[1])] + [job[0].s(job[1]) for job in workflow_chain[1:]])
            res.apply_async()
            return_objects.append(res)

        if not test_status:
            # If we're not doing a test run, update the run count on the workflow
            workflow_obj.runs = run_num

        return Response({"message": workflow_run.get_absolute_url()}, status=status.HTTP_201_CREATED)


class WorkflowRunDetail(generics.RetrieveDestroyAPIView):
    model = WorkflowRun
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = WorkflowRunSerializer
