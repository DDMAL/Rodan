import urlparse
import os
import shutil
from operator import itemgetter
from celery import registry, chain
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
from rodan.serializers.workflowrun import WorkflowRunSerializer, WorkflowRunByPageSerializer
from rodan.serializers.runjob import PageRunJobSerializer, ResultRunJobSerializer
from rodan.helpers.exceptions import WorkFlowTriedTooManyTimesError
from rodan.settings import BACKUP_WORKFLOWRUN_ON_RETRY


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
                                page=page)
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

            if run_job.result.all():
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
        if runjob.workflow_job.workflow is not None:
            # i.e. if the workflow job was never deleted from the workflow
            runjob.job_settings = runjob.workflow_job.job_settings
            runjob.save()
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
            wf_run = WorkflowRun.objects.get(pk=pk)
        except WorkflowRun.DoesNotExist:
            return Response({"message": "Could not resolve ID to workflow object"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            wf_run.workflow
        except Workflow.DoesNotExist:
            return Response({"message": "The WorkflowRun object no longer has a workflow associated with it."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if BACKUP_WORKFLOWRUN_ON_RETRY:
            self._backup_workflowrun(wf_run)

        wf_pages = wf_run.workflow.pages.all()
        wf_runjobs = RunJob.objects.filter(workflow_run=wf_run)
        self._handle_deleted_pages(wf_runjobs, wf_pages)

        for page in wf_pages:
            page_runjobs = wf_runjobs.filter(page=page)
            if not page_runjobs.exists():
                self._handle_new_page(wf_run, page)  # This page has been added later.
                continue

            runjobs_list = sorted(page_runjobs, key=lambda rj: rj.sequence)
            # Sorting like that is troublesome. What if someone edited the workflow in
            # meantime? Two runjobs may now have the same sequence number, and
            # consequently be sorted in the wrong order. The task will then fail.
            # For example, you cannot expect to find pitches before classification.

            # I think, once a workflow has been run once, it should be locked so that the jobs
            # cannot be reordered. Adding new jobs can be permitted, and changing settings
            # is also obviously fine, but reordering the jobs or deleting jobs can
            # seriously screw things up. It should not be allowed.

            # Get the index of the runjob that failed in runjob_list
            # Or get the index of the first job that was cancelled.
            for i, r in enumerate(runjobs_list):
                if r.status in (RunJobStatus.FAILED, RunJobStatus.CANCELLED):
                    failed_index = i
                    break
            else:
                continue  # Looks like nothing failed for this page. Nothing to do here folks.

            self._clean_runjob_folder(runjobs_list[failed_index])

            if failed_index > 0:
                result_id = str(runjobs_list[failed_index - 1].result.get().uuid)
            else:
                result_id = None

            first_job = runjobs_list[failed_index]
            self._update_settings(first_job)
            if first_job.workflow_job.workflow is not None:
                # i.e. if the workflow job was not deleted from the workflow
                first_job.job_settings = first_job.workflow_job.job_settings
                first_job.save()
            first_task = registry.tasks[str(first_job.job_name)]
            task_chain = [first_task.si(result_id, str(first_job.uuid))]

            for job in runjobs_list[failed_index + 1:]:
                rodan_task = registry.tasks[str(first_job.job_name)]
                task_chain.append(rodan_task.s(str(job.uuid)))

            celery_chain = chain(task_chain)
            celery_chain.apply_async()

        return self.retrieve(request, pk, *args, **kwargs)
