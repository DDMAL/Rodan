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
from rest_framework.exceptions import ValidationError

from rodan.models.workflow import Workflow
from rodan.models.runjob import RunJob
from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflowrun import WorkflowRun
from rodan.models.connection import Connection
from rodan.models.resourceassignment import ResourceAssignment
from rodan.models.resource import Resource
from rodan.models.input import Input
from rodan.models.output import Output
from rodan.models.outputport import OutputPort
from rodan.models.inputport import InputPort
from rodan.serializers.user import UserSerializer
from rodan.serializers.workflowrun import WorkflowRunSerializer, WorkflowRunByPageSerializer
from rodan.helpers.exceptions import WorkFlowTriedTooManyTimesError

from rodan.jobs.master_task import master_task
from rodan.constants import task_status

class WorkflowRunList(generics.ListCreateAPIView):
    """
    Returns a list of all WorkflowRuns. Accepts a POST request with a data body to
    create a new WorkflowRun. POST requests will return the newly-created WorkflowRun
    object.

    Creating a new WorkflowRun instance executes the workflow. Meanwhile, RunJobs,
    Inputs, Outputs and Resources are created corresponding to the workflow.

    #### Parameters
    - `workflow` -- GET-only. UUID(GET) or Hyperlink(POST) of a Workflow.


    [TODO]: Deprecated parameters??
    - test=true: Sets whether this is a test run or not. (POST only)
    - page_id=$ID: If this is a test run, you must supply a page ID to test the workflow on. (POST only)
    """
    model = WorkflowRun
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowRunSerializer
    filter_fields = ('workflow',)
    queryset = WorkflowRun.objects.all() # [TODO] filter according to the user?

    def perform_create(self, serializer):
        wfrun_status = serializer.validated_data.get('status', task_status.PROCESSING)
        if wfrun_status != task_status.PROCESSING:
            raise ValidationError({'status': ["Cannot create a cancelled, failed or finished WorkflowRun."]})
        wf = serializer.validated_data['workflow']
        if not wf.valid:
            raise ValidationError({'workflow': ["Workflow must be valid before you can run it."]})

        wfrun = serializer.save(creator=self.request.user)
        wfrun_id = str(wfrun.uuid)
        self._create_workflow_run(wf, wfrun)
        master_task.apply_async((wfrun_id,))

    def _create_workflow_run(self, workflow, workflow_run):
        endpoint_workflowjobs = self._endpoint_workflow_jobs(workflow)
        singleton_workflowjobs = self._singleton_workflow_jobs(workflow)
        workflowjob_runjob_map = {}
        resource_assignments = ResourceAssignment.objects.filter(input_port__workflow_job__workflow=workflow)
        ra_collection = None

        for ra in resource_assignments:
            resources = Resource.objects.filter(resource_assignments=ra)

            if resources.count() > 1:
                ra_collection = ra

        if ra_collection:
            resources = Resource.objects.filter(resource_assignments=ra_collection)

            for res in resources:
                self._runjob_creation_loop(endpoint_workflowjobs, singleton_workflowjobs, workflowjob_runjob_map, workflow_run, res)

        else:
            self._runjob_creation_loop(endpoint_workflowjobs, singleton_workflowjobs, workflowjob_runjob_map, workflow_run, None)

    def _runjob_creation_loop(self, endpoint_workflowjobs, singleton_workflowjobs, workflowjob_runjob_map, workflow_run, arg_resource):
        for wfjob in endpoint_workflowjobs:
            self._create_runjobs(wfjob, workflowjob_runjob_map, workflow_run, arg_resource)

        workflow_job_iteration = {}

        for wfjob in workflowjob_runjob_map:
            workflow_job_iteration[wfjob] = workflowjob_runjob_map[wfjob]

        for wfjob in workflow_job_iteration:
            if wfjob not in singleton_workflowjobs:
                del workflowjob_runjob_map[wfjob]

    def _create_runjobs(self, wfjob_A, workflowjob_runjob_map, workflow_run, arg_resource):
        if wfjob_A in workflowjob_runjob_map:
            return workflowjob_runjob_map[wfjob_A]

        runjob_A = self._create_runjob_A(wfjob_A, workflow_run, arg_resource)

        incoming_connections = Connection.objects.filter(input_port__workflow_job=wfjob_A)

        for conn in incoming_connections:
            wfjob_B = conn.output_workflow_job
            runjob_B = self._create_runjobs(wfjob_B, workflowjob_runjob_map, workflow_run, arg_resource)

            associated_output = Output.objects.get(output_port=conn.output_port,
                                                   run_job=runjob_B)

            Input(run_job=runjob_A,
                  input_port=conn.input_port,
                  resource=associated_output.resource).save()

        # entry inputs
        for ip in InputPort.objects.filter(workflow_job=wfjob_A):
            try:
                ra = ResourceAssignment.objects.get(input_port=ip)

            except ResourceAssignment.DoesNotExist:
                ra = None

            if ra:
                if ra.resources.count() > 1:
                    entry_res = arg_resource
                else:
                    entry_res = ra.resources.first()

                Input(run_job=runjob_A,
                      input_port=ra.input_port,
                      resource=entry_res).save()


        workflowjob_runjob_map[wfjob_A] = runjob_A
        return runjob_A

    def _create_runjob_A(self, wfjob, workflow_run, arg_resource):
        run_job = RunJob(workflow_job=wfjob,
                         workflow_run=workflow_run)
        run_job.save()

        outputports = OutputPort.objects.filter(workflow_job=wfjob).prefetch_related('output_port_type__resource_types')

        for op in outputports:
            resource_type_set = set(op.output_port_type.resource_types.all())
            if op.connections.exists():
                ipt_type_set = set(op.connections.first().input_port.input_port_type.resource_types.all())
                resource_type_set = resource_type_set.intersection(ipt_type_set)
            res_type = resource_type_set.pop()

            resource = Resource(project=workflow_run.workflow.project,
                                resource_type=res_type)
            resource.save()

            output = Output(output_port=op,
                            run_job=run_job,
                            resource=resource)
            output.save()

            if arg_resource:   # resource collection identifier
                resource.name = arg_resource.name
            resource.origin = output
            resource.save()

        return run_job

    def _endpoint_workflow_jobs(self, workflow):
        workflow_jobs = WorkflowJob.objects.filter(workflow=workflow)
        endpoint_workflowjobs = []

        for wfjob in workflow_jobs:
            connections = Connection.objects.filter(output_port__workflow_job=wfjob)

            if not connections:
                endpoint_workflowjobs.append(wfjob)

        return endpoint_workflowjobs

    def _singleton_workflow_jobs(self, workflow):
        singleton_workflowjobs = []

        for wfjob in WorkflowJob.objects.filter(workflow=workflow):
            singleton_workflowjobs.append(wfjob)

        resource_assignments = ResourceAssignment.objects.filter(input_port__workflow_job__workflow=workflow)

        for ra in resource_assignments:
            resources = Resource.objects.filter(resource_assignments=ra)

            if resources.count() > 1:
                initial_wfjob = WorkflowJob.objects.get(input_ports=ra.input_port)
                self._traversal(singleton_workflowjobs, initial_wfjob)

        return singleton_workflowjobs

    def _traversal(self, singleton_workflowjobs, wfjob):
        if wfjob in singleton_workflowjobs:
            singleton_workflowjobs.remove(wfjob)
        adjacent_connections = Connection.objects.filter(output_port__workflow_job=wfjob)
        for conn in adjacent_connections:
            wfjob = WorkflowJob.objects.get(input_ports=conn.input_port)
            self._traversal(singleton_workflowjobs, wfjob)


class WorkflowRunDetail(generics.RetrieveUpdateAPIView):
    """
    Performs operations on a single WorkflowRun instance.

    #### Parameters
    - `status` -- PATCH-only. An integer. Attempt of uncancelling will trigger an error.

    [TODO] are they still effective??

    - `by_page=true`: If true, re-formats the returned workflow run object by returning it based on page-and-results, rather than runjob-and-page.
    - `include_results=true|false`: Sets whether to include the results (per page) for the workflow run (GET only; only checked if `by_page` is present).

    Sending a PATCH request retries the failed jobs in a workflowrun. It tries its best to have expected behavior. If the settings of the associated workflowjob of a runjob is changed, the new settings are picked up by the runjob. Of course, the jobs that have already succeeded will not be run again, so changing their workflowjob settings have no effect whatsoever. If you add a new page to workflow, that page is taken into the workflowrun and all the workflow jobs are run on it, so if you forgot to add one page to a workflow you can add it later and send the patch request to the workflowrun.

    Note that it only tries the workflow starting from the first failed or cancelled job for each page. Under no conditions does it try to rerun a successful job, so for example, if you have already finished segmentation, you do not have to do it again. Also, by default, it will backup all the files of the previous try to MEDIA_ROOT/projects//workflowrun_retry_backup. This behavior is controlled by BACKUP_WORKFLOW_RUN_ON_RETRY variable in settings.py
    """
    model = WorkflowRun
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowRunSerializer
    queryset = WorkflowRun.objects.all() # [TODO] filter according to the user?

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
            # page_data = PageRunJobSerializer(run_job.page, context={'request': request}).data
            k = page_data['url']
            if k not in pages:
                page_data["results"] = []
                pages[k] = page_data

            # [TODO] Remove result
            #if include_results and run_job.result.all():
            #    pages[k]['results'].append(ResultRunJobSerializer(run_job.result.all()[0], context={'request': request}).data)

        workflow_run = WorkflowRunByPageSerializer(workflow_run, context={'request': request}).data[0]
        workflow_run['pages'] = sorted(pages.values(), key=itemgetter('page_order'))

        return Response(workflow_run)

    def perform_update(self, serializer):
        wfrun_id = serializer.data['uuid']
        old_status = WorkflowRun.objects.filter(uuid=wfrun_id).values_list('status', flat=True)[0]
        new_status = serializer.validated_data.get('status', None)

        if old_status == task_status.PROCESSING and new_status == task_status.CANCELLED:
            runjobs_to_revoke_query = RunJob.objects.filter(workflow_run=wfrun_id, status__in=(task_status.SCHEDULED, task_status.PROCESSING))
            runjobs_to_revoke_celery_id = runjobs_to_revoke_query.values_list('celery_task_id', flat=True)

            for celery_id in runjobs_to_revoke_celery_id:
                if celery_id is not None:
                    revoke(celery_id, terminate=True)

            runjobs_to_revoke_query.update(status=task_status.CANCELLED, ready_for_input=False)
        elif new_status is not None:
            raise ValidationError({'status': ["Invalid status update"]})

        serializer.save()

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
        unfinished_runjobs = runjobs.exclude(status=task_status.FINISHED)
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
            is_interactive = workflow_job.job.interactive
            runjob = RunJob(workflow_run=workflow_run,
                            workflow_job=workflow_job,
                            job_settings=workflow_job.job_settings,
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
        ###runjob.needs_input = runjob.workflow_job.job.interactive
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
