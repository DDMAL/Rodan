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


class WorkflowRunViewTest(APITestCase):
    fixtures = ["1_users", "2_initial_data"]

    def setUp(self):
        self.media_root = os.path.join(settings.PROJECT_DIR)

        self.client.login(username="ahankins", password="hahaha")
        page = Page.objects.get(uuid="2f63f986449349769d7a313e0fc6edb3")
        page.page_image = SimpleUploadedFile('original_file.png', 'n/t')
        page.compat_page_image = SimpleUploadedFile('compat_page_image.png', 'n/t')
        page.save()

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
            'workflow': 'http://localhost:8000/workflow/12345/',
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

    def test_get_detail(self):
        response = self.client.get("/workflowrun/eb4b3661be2a44908c4c932b0783bb3e/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list(self):
        response = self.client.get("/workflowruns/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detail_by_page(self):
        response = self.client.get('/workflowrun/eb4b3661be2a44908c4c932b0783bb3e/?by_page=true')
        # self.assertEqual(response)

    def test_patch(self):
        workflowrun_update = {'run': WorkflowRun.objects.get(pk="eb4b3661be2a44908c4c932b0783bb3e").run+1}
        response = self.client.patch("/workflowrun/eb4b3661be2a44908c4c932b0783bb3e/", workflowrun_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_not_found(self):
        workflowrun_update = {'run': 5}
        response = self.client.patch("/workflowrun/12345/", workflowrun_update, format='json')
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
