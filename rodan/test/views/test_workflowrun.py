import os
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

from rodan.models.page import Page
from rodan.models.workflowrun import WorkflowRun
from rodan.models.workflow import Workflow
from rodan.models.runjob import RunJobStatus
from rodan.models.workflowjob import WorkflowJob
from rodan.models.inputport import InputPort
from rodan.models.inputporttype import InputPortType
from rodan.models.outputport import OutputPort
from rodan.models.outputporttype import OutputPortType
from rodan.models.connection import Connection
from rodan.models.job import Job
from rodan.views.workflowrun import WorkflowRunList


class WorkflowRunViewTest(APITestCase):
    fixtures = ["1_users", "2_initial_data"]

    def setUp(self):
        self.media_root = os.path.join(settings.PROJECT_DIR)

        self.client.login(username="ahankins", password="hahaha")
        page = Page.objects.get(uuid="2f63f986449349769d7a313e0fc6edb3")
        page.page_image = SimpleUploadedFile('original_file.png', 'n/t')
        page.compat_page_image = SimpleUploadedFile('compat_page_image.png', 'n/t')
        page.save()

        self.test_workflow = Workflow.objects.get(uuid="ff78a1aa79554abcb5f1b0ac7bba2bad")
        self.test_job = Job.objects.get(uuid="a01a8cb0fea143238946d3d344b65790")
        self.test_user = User.objects.get(username="ahankins")

    def test_post(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/1/',
            'workflow': 'http://localhost:8000/workflow/df78a1aa79554abcb5f1b0ac7bba2bad/',
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        wfr = {
            'creator': User.objects.get(pk=1),
            'workflow': Workflow.objects.get(pk='df78a1aa79554abcb5f1b0ac7bba2bad')
        }
        workflow_run = WorkflowRun(**wfr)
        workflow_run.save()
        self.assertEqual(workflow_run.workflow, wfr['workflow'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_no_workflow_ID(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/1/',
            'workflow': None,
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {"message": "You must specify a workflow ID"}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_no_existing_workflow(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/1',
            'workflow': 'http://localhost:8000/workflow/df78a1aa79554abcb5f1b0ac7bba2bac/',
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {"message": "You must specify an existing workflow"}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_no_jobs(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/1/',
            'workflow': 'http://localhost:8000/workflow/ef78a1aa79554abcb5f1b0ac7bba2bad/',
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {"message": "No jobs for workflow {0} were specified".format(workflowrun_obj['workflow'])}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_no_pages(self):
        workflowrun_obj = {
            'creator': 'http://localhost:8000/user/1/',
            'workflow': 'http://localhost:8000/workflow/ff78a1aa79554abcb5f1b0ac7bba2bad/',
        }

        response = self.client.post("/workflowruns/", workflowrun_obj, format='json')
        anticipated_message = {"message": "No pages were assigned to workflow ID {0}".format(workflowrun_obj['workflow'])}
        self.assertEqual(response.data, anticipated_message)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_branching_workflow(self):
        test_second_output_workflowjob = WorkflowJob(workflow=self.test_workflow, job=self.test_job)
        test_second_output_workflowjob.save()

        test_workflowjob2 = WorkflowJob.objects.get(uuid="a21f510a16c24701ac0e435b3f4c20f3")

        test_outputporttype = OutputPortType.objects.get(uuid="1cdb067e98194da48dd3dfa35e84671c")
        test_outputport = OutputPort(workflow_job=test_workflowjob2, output_port_type=test_outputporttype)
        test_outputport.save()

        test_workflowjob3 = WorkflowJob(workflow=self.test_workflow, job=self.test_job)
        test_workflowjob3.save()

        test_inputporttype = InputPortType.objects.get(uuid="30ed42546fe440a181f64a2ebdea82e1")
        test_inputport_for_workflowjob3 = InputPort(workflow_job=test_workflowjob3, input_port_type=test_inputporttype)
        test_inputport_for_workflowjob3.save()

        test_second_inputport = InputPort(workflow_job=test_second_output_workflowjob, input_port_type=test_inputporttype)
        test_second_inputport.save()

        test_end_output_port = OutputPort(workflow_job=test_second_output_workflowjob, output_port_type=test_outputporttype)
        test_end_output_port.save()

        test_outputport_for_workflowjob3 = OutputPort(workflow_job=test_workflowjob3, output_port_type=test_outputporttype)
        test_outputport_for_workflowjob3.save()

        connection2_data = {
            'input_port': test_second_inputport,
            'input_workflow_job': test_second_output_workflowjob,
            'output_port': test_outputport,
            'output_workflow_job': test_workflowjob2,
            'workflow': self.test_workflow,
        }
        test_connection2 = Connection(**connection2_data)
        test_connection2.save()

        connection3_data = {
            'input_port': test_inputport_for_workflowjob3,
            'input_workflow_job': test_workflowjob3,
            'output_port': OutputPort.objects.get(uuid="0e8b037c44f74364a60a7f5cc397a48d"),
            'output_workflow_job': test_workflowjob2,
            'workflow': self.test_workflow,
        }
        test_connection3 = Connection(**connection3_data)
        test_connection3.save()

        endpoints = WorkflowRunList._endpoint_workflow_jobs(WorkflowRunList(), self.test_workflow)
        end_jobs = [test_second_output_workflowjob, test_workflowjob3]
        self.assertEqual(endpoints, end_jobs)

        singletons = WorkflowRunList._singleton_workflow_jobs(WorkflowRunList(), self.test_workflow)
        self.assertFalse(singletons)

        workflow_run = WorkflowRun(workflow=self.test_workflow,
                                   creator=self.test_user)

        WorkflowRunList._create_workflow_run(WorkflowRunList(), self.test_workflow, workflow_run)

    def test_endpoint_workflow_jobs(self):
        endpoints = WorkflowRunList._endpoint_workflow_jobs(WorkflowRunList(), self.test_workflow)
        self.assertEqual(endpoints, [WorkflowJob.objects.get(uuid="a21f510a16c24701ac0e435b3f4c20f3")])

    def test_singleton_workflow_jobs(self):
        single_workflowjob = WorkflowJob(workflow=self.test_workflow, job=self.test_job)
        single_workflowjob.save()

        test_outputporttype = OutputPortType.objects.get(uuid="1cdb067e98194da48dd3dfa35e84671c")
        single_outputport = OutputPort(workflow_job=single_workflowjob, output_port_type=test_outputporttype)
        single_outputport.save()

        test_workflowjob2 = WorkflowJob.objects.get(uuid="a21f510a16c24701ac0e435b3f4c20f3")

        test_inputporttype = InputPortType.objects.get(uuid="30ed42546fe440a181f64a2ebdea82e1")
        test_second_inputport = InputPort(workflow_job=test_workflowjob2, input_port_type=test_inputporttype)
        test_second_inputport.save()

        connection2_data = {
            'input_port': test_second_inputport,
            'input_workflow_job':test_workflowjob2,
            'output_port': single_outputport,
            'output_workflow_job': single_workflowjob,
            'workflow': self.test_workflow,
        }
        test_connection2 = Connection(**connection2_data)
        test_connection2.save()

        singletons = WorkflowRunList._singleton_workflow_jobs(WorkflowRunList(), self.test_workflow)
        self.assertEqual(singletons, [single_workflowjob])

    def test_get_detail(self):
        response = self.client.get("/workflowrun/eb4b3661be2a44908c4c932b0783bb3e/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list(self):
        response = self.client.get("/workflowruns/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch(self):
        workflowrun_update = {'run': WorkflowRun.objects.get(pk="eb4b3661be2a44908c4c932b0783bb3e").run+1}
        response = self.client.patch("/workflowrun/eb4b3661be2a44908c4c932b0783bb3e/", workflowrun_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_not_found(self):
        workflowrun_update = {'run': 5}
        response = self.client.patch("/workflowrun/df78a1aa79554abcb5f1b0ac7bba2bac/", workflowrun_update, format='json')
        anticipated_message = {'message': 'Workflow_run not found'}
        self.assertEqual(anticipated_message, response.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_already_cancelled(self):
        workflowrun_update = {'cancelled': False}
        response = self.client.patch("/workflowrun/4b1a0d13b2cd48a5a99324d7308ca27a/", workflowrun_update, format='json')
        anticipated_message = {"message": "Workflowrun cannot be uncancelled."}
        self.assertEqual(anticipated_message, response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_newly_cancelled(self):
        workflowrun_update = {'cancelled': True}
        self.client.patch("/workflowrun/eb4b3661be2a44908c4c932b0783bb3e/", workflowrun_update, format='json')
        workflowrun_obj = WorkflowRun.objects.get(pk='eb4b3661be2a44908c4c932b0783bb3e')
        expected_status = RunJobStatus.CANCELLED or RunJobStatus.HAS_FINISHED or RunJobStatus.FAILED
        for rj in workflowrun_obj.run_jobs.all():
            self.assertEqual(rj.status, expected_status)
