import urlparse
import os
import shutil
from operator import itemgetter
from celery import registry, chain
from celery.task.control import revoke
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
from rodan.models.runjob import RunJobStatus
from rodan.models.connection import Connection
from rodan.models.resourceassignment import ResourceAssignment
from rodan.models.resource import Resource
from rodan.models.input import Input
from rodan.models.output import Output
from rodan.models.outputport import OutputPort
from rodan.serializers.workflowrun import WorkflowRunSerializer, WorkflowRunByPageSerializer
from rodan.serializers.runjob import PageRunJobSerializer, ResultRunJobSerializer
from rodan.helpers.exceptions import WorkFlowTriedTooManyTimesError


class WorkflowRunList(generics.ListCreateAPIView):
    model = WorkflowRun
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowRunSerializer
    paginate_by = None

    def get_queryset(self):
        workflow = self.request.QUERY_PARAMS.get('workflow', None)
        run = self.request.QUERY_PARAMS.get('run', None)

        queryset = WorkflowRun.objects.all()

        if workflow:
            queryset = queryset.filter(workflow__uuid=workflow)

        if run:
            queryset = queryset.filter(run=run)

        return queryset

    def _create_workflow_run(self, workflow, workflow_run):
        endpoint_workflowjobs = self._endpoint_workflow_jobs(workflow)
        singleton_workflowjobs = self._singleton_workflow_jobs(workflow)
        workflowjob_runjob_map = {}
        resource_assignments = ResourceAssignment.objects.filter(workflow=workflow)

        for ra in resource_assignments:
            resources = Resource.objects.filter(resource_assignments=ra)
            if resources.count() < 2:
                break

            for res in resources:
                self._runjob_creation_loop(endpoint_workflowjobs, singleton_workflowjobs, workflowjob_runjob_map, workflow_run, res)
                return None

        self._runjob_creation_loop(endpoint_workflowjobs, singleton_workflowjobs, workflowjob_runjob_map, workflow_run)

    def _runjob_creation_loop(self, endpoint_workflowjobs, singleton_workflowjobs, workflowjob_runjob_map, workflow_run, resource):
        for wfjob in endpoint_workflowjobs:
            self._create_runjobs(wfjob, workflowjob_runjob_map, workflow_run, resource)
            self._remove_non_singletons(workflowjob_runjob_map, singleton_workflowjobs)

    def _remove_non_singletons(self, workflowjob_runjob_map, singleton_workflowjobs):
        for wfjob in workflowjob_runjob_map:
            if wfjob not in singleton_workflowjobs:
                workflowjob_runjob_map.remove(wfjob)

    def _create_runjobs(self, wfjob_A, workflowjob_runjob_map, workflow_run, resource):
        if wfjob_A in workflowjob_runjob_map:
            return None

        runjob_A = self._create_runjob_A(wfjob_A, workflow_run)

        incoming_connections = Connection.objects.filter(input_workflow_job=wfjob_A)

        for conn in incoming_connections:
            wfjob_B = conn.output_workflow_job
            self._create_runjobs(wfjob_B, workflowjob_runjob_map, workflow_run, resource)
            if wfjob_B in workflowjob_runjob_map:
                return None

            associated_output = Output.objects.filter(output_port=conn.output_port).order_by('-created')[0]

            Input(run_job=runjob_A,
                  input_port=conn.input_port,
                  resource=associated_output.resource).save()

        try:
            resource_assignments = ResourceAssignment.objects.get(workflow_job=wfjob_A)

        except ResourceAssignment.DoesNotExist:
            return None

        for ra in resource_assignments:
            Input(run_job=runjob_A,
                  input_port=ra.input_port,
                  resource=resource).save()

        workflowjob_runjob_map.append({runjob_A: wfjob_A})

    def _create_runjob_A(self, wfjob, workflow_run):
        run_job = RunJob(workflow_job=wfjob,
                         workflow_run=workflow_run)
        run_job.save()

        outputports = OutputPort.objects.filter(workflow_job=wfjob)

        for op in outputports:
            resource = Resource(project=workflow_run.workflow.project,
                                resource_type=op.output_port_type.resource_type,
                                workflow=workflow_run.workflow)
            resource.save()

            Output(output_port=op,
                   run_job=run_job,
                   resource=resource).save()

        return run_job

    def _endpoint_workflow_jobs(self, workflow):
        workflow_jobs = WorkflowJob.objects.filter(workflow=workflow)
        endpoint_workflowjobs = []

        for wfjob in workflow_jobs:
            connections = Connection.objects.filter(output_workflow_job=wfjob)

            if not connections:
                endpoint_workflowjobs.append(wfjob)

        return endpoint_workflowjobs

    def _singleton_workflow_jobs(self, workflow):
        singleton_workflowjobs = []

        for wfjob in WorkflowJob.objects.filter(workflow=workflow):
            singleton_workflowjobs.append(wfjob)

        resource_assignments = ResourceAssignment.objects.filter(workflow=workflow)

        for ra in resource_assignments:
            resources = Resource.objects.filter(resource_assignments=ra)

            if resources.count() > 1:
                initial_wfjob = WorkflowJob.objects.get(inputport=ra.input_port)
                self._traversal(singleton_workflowjobs, initial_wfjob)

        return singleton_workflowjobs

    def _traversal(self, singleton_workflowjobs, wfjob):
        singleton_workflowjobs.remove(wfjob)
        adjacent_connections = Connection.objects.filter(output_workflow_job=wfjob)

        if not adjacent_connections:
            return None

        for conn in adjacent_connections:
            wfjob = WorkflowJob.objects.get(inputport=conn.input_port)
            self._traversal(singleton_workflowjobs, wfjob)

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

        workflow_run = WorkflowRun(creator=request.user,
                                   workflow=workflow_obj)
        workflow_run.save()

        if test_status:
            # running in test mode. This runs the workflow on a single page.
            if not page_id:
                return Response({"message": "You must specify a page ID if you are running in test mode."}, status=status.HTTP_400_BAD_REQUEST)

            value = urlparse.urlparse(page_id).path
            try:
                p = resolve(value)
            except:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

            pages = Page.objects.filter(pk=p.kwargs.get('pk'))
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

        workflow_run = WorkflowRun(workflow=workflow_obj,
                                   run=run_num,
                                   test_run=test_status,
                                   creator=request.user)

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
                                sequence=workflow_job.sequence)

                runjob.save()

                rodan_task = registry.tasks[str(workflow_job.job_name)]
                workflow_chain.append((rodan_task, str(runjob.uuid)))
            first_job = workflow_chain[0]
            res = chain([first_job[0].si(None, first_job[1])] + [job[0].s(job[1]) for job in workflow_chain[1:]])
            res.apply_async()
            return_objects.append(res)

        if not test_status:
            # If we're not doing a test run, update the run count on the workflow
            workflow_obj.runs = run_num

        return Response({"message": workflow_run.get_absolute_url()}, status=status.HTTP_201_CREATED)


class WorkflowRunDetail(generics.RetrieveUpdateDestroyAPIView):
    model = WorkflowRun
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowRunSerializer

    def get(self, request, pk, *args, **kwargs):
        by_page = self.request.QUERY_PARAMS.get('by_page', None)
        include_results = self.request.QUERY_PARAMS.get('include_results', None)
        if not by_page:
            return self.retrieve(request, pk, *args, **kwargs)

        # If we have ?by_page=true set, we should return the results
        # by page, rather than by run_job. This makes it easier to display
        # the results on a page-by-page basis.
        workflow_run = WorkflowRun.objects.filter(pk=pk).select_related()
        run_jobs = workflow_run[0].run_jobs.all()
        pages = {}
        for run_job in run_jobs:
            page_data = PageRunJobSerializer(run_job.page, context={'request': request}).data
            k = page_data['url']
            if k not in pages:
                page_data["results"] = []
                pages[k] = page_data

            if include_results and run_job.result.all():
                pages[k]['results'].append(ResultRunJobSerializer(run_job.result.all()[0], context={'request': request}).data)

        workflow_run = WorkflowRunByPageSerializer(workflow_run, context={'request': request}).data[0]
        workflow_run['pages'] = sorted(pages.values(), key=itemgetter('page_order'))

        return Response(workflow_run)

    def _backup_workflowrun(self, wf_run):
        source = wf_run.workflow_run_path
        wf_backup_dir = wf_run.retry_backup_directory
        dir_name_base = str(wf_run.uuid)
        for i in range(1, 1000):
            test_dir_name = "%s_%d" % (dir_name_base, i)
            test_dest = os.path.join(wf_backup_dir, test_dir_name)
            if not os.path.exists(test_dest):
                dir_name = test_dir_name
                break
        else:
            raise WorkFlowTriedTooManyTimesError("You have tried this workflow 1000 times. Stop.")

        destination = os.path.join(wf_backup_dir, dir_name)
        shutil.copytree(source, destination)

    def _handle_deleted_pages(self, runjobs, pages):
        unfinished_runjobs = runjobs.exclude(status=RunJobStatus.HAS_FINISHED)
        for rj in unfinished_runjobs:
            if rj.page not in pages:
                rj.error_summary = "Page Deleted"
                rj.error_details = "Looks like you have deleted this page from the workflow. The job cannot be rerun. You will have to add the acossiated page back into the workflow if you want to retry this job."
                rj.save()

    def _handle_new_page(self, workflow_run, page):
        """
        For the pages that has been added later but were not there during the original
        run, we simply run the all the jobs in the workflow. The problem is, if someone
        edited the workflow in the meantime, the new workflow jobs will be run against
        the new pages, not the old workflow jobs.
        """
        # This method should be refactored. I literally copied code from up there.
        # Maybe *after* I write some unit tests?
        workflow_jobs = workflow_run.workflow.workflow_jobs.all()

        workflow_chain = []
        for workflow_job in workflow_jobs:
            is_interactive = False if workflow_job.job_type == 0 else True
            runjob = RunJob(workflow_run=workflow_run,
                            workflow_job=workflow_job,
                            job_settings=workflow_job.job_settings,
                            needs_input=is_interactive,
                            page=page)
            runjob.save()

            rodan_task = registry.tasks[str(workflow_job.job_name)]
            workflow_chain.append((rodan_task, str(runjob.uuid)))
        first_job = workflow_chain[0]
        res = chain([first_job[0].si(None, first_job[1])] + [job[0].s(job[1]) for job in workflow_chain[1:]])
        res.apply_async()

    def _clean_runjob_folder(self, runjob):
        if os.path.exists(runjob.runjob_path):
            shutil.rmtree(runjob.runjob_path)
        os.makedirs(runjob.runjob_path)

    def _update_settings(self, runjob):
        runjob.needs_input = runjob.workflow_job.job.interactive
        if runjob.workflow_job.workflow is not None:
            # i.e. if the workflow job was never deleted from the workflow
            runjob.job_settings = runjob.workflow_job.job_settings
        else:
            # We're trying to find a new workflow_job with the job_name.
            new_workflowjobs = runjob.workflow_run.workflow.workflow_jobs.filter(job__job_name=runjob.job_name)
            if new_workflowjobs.exists():
                runjob.job_settings = new_workflowjobs[0].job_settings  # We just grab the first matching one.
                runjob.workflowjob = new_workflowjobs[0]  # And also set the new workflow_job.
                                                          # I'm not too sure about this one.
        runjob.save()

    def patch(self, request, pk, *args, **kwargs):
        try:
            workflow_run = WorkflowRun.objects.get(pk=pk)
        except WorkflowRun.DoesNotExist:
            return Response({'message': "Workflow_run not found"}, status=status.HTTP_404_NOT_FOUND)

        workflow_already_cancelled = workflow_run.cancelled
        workflow_newly_cancelled = request.DATA.get('cancelled', None)

        if not workflow_already_cancelled and workflow_newly_cancelled:
            runjobs = workflow_run.run_jobs.all()
            for rj in runjobs:
                if rj.status not in (RunJobStatus.HAS_FINISHED, RunJobStatus.FAILED):
                    if rj.status == RunJobStatus.RUNNING:
                        revoke(rj.celery_task_id, terminate=True)
                    rj.status = RunJobStatus.CANCELLED
                    rj.save()

        if workflow_already_cancelled and workflow_newly_cancelled == False:
            return Response({"message": "Workflowrun cannot be uncancelled."}, status=status.HTTP_400_BAD_REQUEST)

        return self.partial_update(request, pk, *args, **kwargs)
